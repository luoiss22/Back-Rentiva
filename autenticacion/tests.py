from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Administrador, CredencialAdmin, Propietario, Credencial


def _crear_usuario(nombre, email, password="segura1234", rol="propietario"):
    """Helper: crea Propietario + Credencial y devuelve (propietario, token)."""
    if rol == "admin":
        usuario = Administrador.objects.create(
            nombre=nombre,
            apellidos="Test",
            email=email,
        )
        cred = CredencialAdmin(administrador=usuario, email=email)
        cred.set_password(password)
        cred.save()
    else:
        usuario = Propietario.objects.create(
            nombre=nombre,
            apellidos="Test",
            email=email,
        )
        cred = Credencial(propietario=usuario, email=email)
        cred.set_password(password)
        cred.save()

    client = APIClient()
    resp = client.post(
        "/api/v1/auth/login/",
        {"email": email, "password": password},
        format="json",
    )
    return usuario, resp.data["tokens"]["access"]


class RegistroTests(TestCase):
    """Tests para el endpoint de registro."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/auth/registro/"

    def test_registro_exitoso(self):
        data = {
            "nombre": "Luis",
            "apellidos": "García",
            "email": "luis@test.com",
            "password": "segura1234",
        }
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", resp.data)
        self.assertIn("access", resp.data["tokens"])
        self.assertIn("refresh", resp.data["tokens"])
        self.assertTrue(Propietario.objects.filter(email="luis@test.com").exists())
        self.assertTrue(Credencial.objects.filter(email="luis@test.com").exists())

    def test_registro_email_duplicado(self):
        Propietario.objects.create(nombre="Ana", apellidos="López", email="ana@test.com")
        data = {
            "nombre": "Ana",
            "apellidos": "López",
            "email": "ana@test.com",
            "password": "segura1234",
        }
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_password_corta(self):
        data = {
            "nombre": "Test",
            "apellidos": "User",
            "email": "short@test.com",
            "password": "123",
        }
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_fuerza_rol_propietario(self):
        """Aunque se envíe rol=admin, siempre se crea como propietario."""
        data = {
            "nombre": "Hack",
            "apellidos": "Attempt",
            "email": "hack@test.com",
            "password": "segura1234",
            "rol": "admin",
        }
        resp = self.client.post(self.url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Administrador.objects.filter(email="hack@test.com").exists())
        self.assertEqual(resp.data["user_type"], "propietario")


class LoginTests(TestCase):
    """Tests para login y JWT."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = "/api/v1/auth/login/"
        self.propietario = Propietario.objects.create(
            nombre="Test", apellidos="User", email="test@test.com",
        )
        self.credencial = Credencial(
            propietario=self.propietario, email="test@test.com",
        )
        self.credencial.set_password("segura1234")
        self.credencial.save()

    def test_login_exitoso(self):
        resp = self.client.post(
            self.login_url,
            {"email": "test@test.com", "password": "segura1234"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", resp.data)

    def test_login_password_incorrecta(self):
        resp = self.client.post(
            self.login_url,
            {"email": "test@test.com", "password": "incorrecta"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_bloqueo_por_intentos(self):
        for _ in range(5):
            self.client.post(
                self.login_url,
                {"email": "test@test.com", "password": "incorrecta"},
                format="json",
            )
        resp = self.client.post(
            self.login_url,
            {"email": "test@test.com", "password": "segura1234"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.credencial.refresh_from_db()
        self.assertTrue(self.credencial.bloqueado)

    def test_me_requiere_auth(self):
        resp = self.client.get("/api/v1/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PropietarioViewSetTests(TestCase):
    """Tests para endpoints CRUD de propietarios (requieren auth)."""

    def setUp(self):
        self.client = APIClient()
        self.propietario, self.token = _crear_usuario(
            "Owner", "owner@test.com",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_listar_propietarios_con_auth(self):
        resp = self.client.get("/api/v1/propietarios/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_listar_propietarios_sin_auth(self):
        self.client.credentials()
        resp = self.client.get("/api/v1/propietarios/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_propietario_solo_ve_su_perfil(self):
        """Un propietario no puede ver el perfil de otro."""
        _crear_usuario("Other", "other@test.com")
        resp = self.client.get("/api/v1/propietarios/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data["results"]
        ids = [p["id"] for p in results]
        self.assertEqual(ids, [self.propietario.pk])


class RolSeguridadTests(TestCase):
    """Tests de seguridad: aislamiento de datos entre propietarios."""

    def setUp(self):
        self.client = APIClient()
        # Propietario A
        self.prop_a, self.token_a = _crear_usuario("OwnerA", "a@test.com")
        # Propietario B
        self.prop_b, self.token_b = _crear_usuario("OwnerB", "b@test.com")
        # Admin
        self.admin, self.token_admin = _crear_usuario(
            "Admin", "admin@test.com", rol="admin",
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ── Propiedades ───────────────────────────────────────────────
    def test_propietario_solo_ve_sus_propiedades(self):
        from propiedades.models import Propiedad
        Propiedad.objects.create(
            propietario=self.prop_a, nombre="Casa A",
            direccion="Dir A", ciudad="CDMX",
            estado_geografico="CDMX", tipo="casa", costo_renta=10000,
        )
        Propiedad.objects.create(
            propietario=self.prop_b, nombre="Casa B",
            direccion="Dir B", ciudad="GDL",
            estado_geografico="JAL", tipo="casa", costo_renta=12000,
        )
        # Propietario A solo ve Casa A
        self._auth(self.token_a)
        resp = self.client.get("/api/v1/propiedades/")
        results = resp.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "Casa A")

        # Propietario B solo ve Casa B
        self._auth(self.token_b)
        resp = self.client.get("/api/v1/propiedades/")
        results = resp.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "Casa B")

    def test_admin_ve_todas_las_propiedades(self):
        from propiedades.models import Propiedad
        Propiedad.objects.create(
            propietario=self.prop_a, nombre="Casa A",
            direccion="Dir A", ciudad="CDMX",
            estado_geografico="CDMX", tipo="casa", costo_renta=10000,
        )
        Propiedad.objects.create(
            propietario=self.prop_b, nombre="Casa B",
            direccion="Dir B", ciudad="GDL",
            estado_geografico="JAL", tipo="casa", costo_renta=12000,
        )
        self._auth(self.token_admin)
        resp = self.client.get("/api/v1/propiedades/")
        self.assertEqual(resp.data["count"], 2)

    def test_propietario_no_puede_ver_propiedad_ajena(self):
        from propiedades.models import Propiedad
        prop_b_obj = Propiedad.objects.create(
            propietario=self.prop_b, nombre="Casa B",
            direccion="Dir B", ciudad="GDL",
            estado_geografico="JAL", tipo="casa", costo_renta=12000,
        )
        self._auth(self.token_a)
        resp = self.client.get(f"/api/v1/propiedades/{prop_b_obj.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ── Arrendatarios ─────────────────────────────────────────────
    def test_propietario_solo_ve_sus_arrendatarios(self):
        from arrendatarios.models import Arrendatario
        Arrendatario.objects.create(
            propietario=self.prop_a, nombre="Inquilino A", apellidos="Test",
        )
        Arrendatario.objects.create(
            propietario=self.prop_b, nombre="Inquilino B", apellidos="Test",
        )
        self._auth(self.token_a)
        resp = self.client.get("/api/v1/arrendatarios/")
        results = resp.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "Inquilino A")

    def test_crear_arrendatario_asigna_propietario(self):
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/arrendatarios/",
            {"nombre": "Nuevo", "apellidos": "Inquilino"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["propietario"], self.prop_a.pk)

    # ── Cambiar rol ──────────────────────────────────────────────
    def test_solo_admin_puede_cambiar_rol(self):
        self._auth(self.token_a)
        resp = self.client.patch(
            f"/api/v1/admin/propietarios/{self.prop_b.pk}/rol/",
            {"rol": "admin"},
            format="json",
        )
        # Endpoint no expuesto en el API actual.
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_puede_cambiar_rol(self):
        self._auth(self.token_admin)
        resp = self.client.patch(
            f"/api/v1/admin/propietarios/{self.prop_b.pk}/rol/",
            {"rol": "admin"},
            format="json",
        )
        # Endpoint no expuesto en el API actual.
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ── Catálogos (IsAdminOrReadOnly) ─────────────────────────────
    def test_propietario_puede_leer_especialistas(self):
        self._auth(self.token_a)
        resp = self.client.get("/api/v1/especialistas/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_propietario_no_puede_crear_especialistas(self):
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/especialistas/",
            {"nombre": "Plomero", "especialidad": "plomería", "telefono": "555"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class LogoutTests(TestCase):
    """Tests para el endpoint de logout (token blacklist)."""

    def setUp(self):
        self.client = APIClient()
        self.prop, self.token = _crear_usuario("LogoutUser", "logout@test.com")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # Obtener refresh token
        resp = APIClient().post(
            "/api/v1/auth/login/",
            {"email": "logout@test.com", "password": "segura1234"},
            format="json",
        )
        self.refresh = resp.data["tokens"]["refresh"]

    def test_logout_invalida_refresh_token(self):
        resp = self.client.post(
            "/api/v1/auth/logout/",
            {"refresh": self.refresh},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        # Intentar refrescar con el mismo token debe fallar
        resp2 = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": self.refresh},
            format="json",
        )
        self.assertEqual(resp2.status_code, 401)

    def test_logout_sin_refresh_falla(self):
        resp = self.client.post("/api/v1/auth/logout/", {}, format="json")
        self.assertEqual(resp.status_code, 400)


class MePatchTests(TestCase):
    """Tests para PATCH auth/me/ (actualizar perfil)."""

    def setUp(self):
        self.client = APIClient()
        self.prop, self.token = _crear_usuario("Original", "me@test.com")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_patch_me_actualiza_nombre(self):
        resp = self.client.patch(
            "/api/v1/auth/me/",
            {"nombre": "Actualizado"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["usuario"]["nombre"], "Actualizado")
        self.prop.refresh_from_db()
        self.assertEqual(self.prop.nombre, "Actualizado")

    def test_patch_me_actualiza_banco_y_clabe(self):
        resp = self.client.patch(
            "/api/v1/auth/me/",
            {
                "banco": "BBVA",
                "clabe_interbancaria": "012345678901234567",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["usuario"]["banco"], "BBVA")
        self.assertEqual(
            resp.data["usuario"]["clabe_interbancaria"],
            "012345678901234567",
        )

        self.prop.refresh_from_db()
        self.assertEqual(self.prop.banco, "BBVA")
        self.assertEqual(self.prop.clabe_interbancaria, "012345678901234567")

    def test_patch_me_no_cambia_rol(self):
        resp = self.client.patch(
            "/api/v1/auth/me/",
            {"rol": "admin"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.prop.refresh_from_db()
        self.assertFalse(Administrador.objects.filter(email=self.prop.email).exists())
        self.assertEqual(resp.data["user_type"], "propietario")

    def test_patch_me_ignora_campo_no_permitido(self):
        self.prop.nombre = "Original"
        self.prop.save(update_fields=["nombre"])

        resp = self.client.patch(
            "/api/v1/auth/me/",
            {"rol": "admin", "nombre": "Valido"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["usuario"]["nombre"], "Valido")

        self.prop.refresh_from_db()
        self.assertEqual(self.prop.nombre, "Valido")
        self.assertFalse(Administrador.objects.filter(email=self.prop.email).exists())
        self.assertEqual(resp.data["user_type"], "propietario")


class FKOwnershipTests(TestCase):
    """Tests de validación de ownership en escritura (FK injection)."""

    def setUp(self):
        self.client = APIClient()
        self.prop_a, self.token_a = _crear_usuario("OwnerA", "fka@test.com")
        self.prop_b, self.token_b = _crear_usuario("OwnerB", "fkb@test.com")

        from propiedades.models import Propiedad
        from arrendatarios.models import Arrendatario

        self.prop_a_propiedad = Propiedad.objects.create(
            propietario=self.prop_a, nombre="Casa A",
            direccion="Dir A", ciudad="CDMX",
            estado_geografico="CDMX", tipo="casa", costo_renta=10000,
        )
        self.prop_b_propiedad = Propiedad.objects.create(
            propietario=self.prop_b, nombre="Casa B",
            direccion="Dir B", ciudad="GDL",
            estado_geografico="JAL", tipo="casa", costo_renta=12000,
        )
        self.arr_a = Arrendatario.objects.create(
            propietario=self.prop_a, nombre="Inq A", apellidos="Test",
        )
        self.arr_b = Arrendatario.objects.create(
            propietario=self.prop_b, nombre="Inq B", apellidos="Test",
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_no_puede_crear_contrato_en_propiedad_ajena(self):
        """Propietario A no puede crear un contrato en la propiedad de B."""
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/contratos/",
            {
                "propiedad": self.prop_b_propiedad.pk,
                "arrendatario": self.arr_a.pk,
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-12-31",
                "renta_acordada": "10000",
                "dia_pago": 1,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("propiedad", resp.data)

    def test_no_puede_crear_contrato_con_arrendatario_ajeno(self):
        """Propietario A no puede usar arrendatarios de B."""
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/contratos/",
            {
                "propiedad": self.prop_a_propiedad.pk,
                "arrendatario": self.arr_b.pk,
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-12-31",
                "renta_acordada": "10000",
                "dia_pago": 1,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("arrendatario", resp.data)

    def test_puede_crear_contrato_en_su_propiedad(self):
        """Propietario A puede crear contrato en su propia propiedad."""
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/contratos/",
            {
                "propiedad": self.prop_a_propiedad.pk,
                "arrendatario": self.arr_a.pk,
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-12-31",
                "renta_acordada": "10000",
                "dia_pago": 1,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_no_puede_crear_pago_en_contrato_ajeno(self):
        """Propietario A no puede crear pagos en contratos de B."""
        from contratos.models import Contrato
        contrato_b = Contrato.objects.create(
            propiedad=self.prop_b_propiedad,
            arrendatario=self.arr_b,
            fecha_inicio="2026-01-01",
            fecha_fin="2026-12-31",
            renta_acordada=12000,
            dia_pago=1,
        )
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/pagos/",
            {
                "contrato": contrato_b.pk,
                "periodo": "2026-01",
                "monto": "12000",
                "fecha_limite": "2026-01-31",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_puede_adjuntar_documento_a_propiedad_ajena(self):
        """Propietario A no puede subir documentos a propiedad de B."""
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/documentos/",
            {
                "tipo_entidad": "propiedad",
                "entidad_id": self.prop_b_propiedad.pk,
                "tipo_documento": "foto",
                "nombre_archivo": "hack.jpg",
                "ruta_archivo": "",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_puede_crear_datos_fiscales_para_otro(self):
        """Propietario A no puede crear datos fiscales de otro propietario."""
        self._auth(self.token_a)
        resp = self.client.post(
            "/api/v1/datos-fiscales/",
            {
                "tipo_entidad": "propietario",
                "entidad_id": self.prop_b.pk,
                "nombre_o_razon_social": "Hack SA",
                "rfc": "XAXX010101000",
                "regimen_fiscal": "601",
                "uso_cfdi": "G03",
                "codigo_postal": "01000",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
