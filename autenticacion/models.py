from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class AuthUserMixin:
    """
    Mixin que satisface la interfaz minima que DRF espera en request.user.
    """

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


# ── ADMINISTRADOR ──────────────────────────────────────────────────


class Administrador(AuthUserMixin, models.Model):
    """Usuario interno de la empresa que gestiona la plataforma."""

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        SUSPENDIDO = "suspendido", "Suspendido"

    nombre = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    folio_ine = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to="administradores/fotos/", blank=True, null=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campo para que permissions/views puedan distinguir facilmente
    USER_TYPE = "admin"

    class Meta:
        db_table = "administradores"
        ordering = ["-created_at"]
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


class CredencialAdmin(models.Model):
    """Credenciales de acceso del administrador."""

    administrador = models.OneToOneField(
        Administrador,
        on_delete=models.CASCADE,
        related_name="credencial",
    )
    email = models.EmailField(unique=True)
    contrasena_hash = models.CharField(max_length=255)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.PositiveIntegerField(default=0)
    bloqueado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "credenciales_admin"
        verbose_name = "Credencial de administrador"
        verbose_name_plural = "Credenciales de administradores"

    def __str__(self):
        return f"Credencial → {self.administrador}"

    def set_password(self, raw_password: str):
        self.contrasena_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.contrasena_hash)


# ── PROPIETARIO ────────────────────────────────────────────────────


class Propietario(AuthUserMixin, models.Model):
    """Propietario / arrendador de inmuebles (cliente de la plataforma)."""

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        SUSPENDIDO = "suspendido", "Suspendido"

    nombre = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    folio_ine = models.CharField(max_length=20, blank=True)
    banco = models.CharField(max_length=100, blank=True)
    clabe_interbancaria = models.CharField("CLABE interbancaria", max_length=18, blank=True)
    foto = models.ImageField(upload_to="propietarios/fotos/", blank=True, null=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campo para que permissions/views puedan distinguir facilmente
    USER_TYPE = "propietario"

    class Meta:
        db_table = "propietarios"
        ordering = ["-created_at"]
        verbose_name = "Propietario"
        verbose_name_plural = "Propietarios"

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


class Credencial(models.Model):
    """Credenciales de acceso del propietario."""

    propietario = models.OneToOneField(
        Propietario,
        on_delete=models.CASCADE,
        related_name="credencial",
    )
    email = models.EmailField(unique=True)
    contrasena_hash = models.CharField(max_length=255)
    token_recuperacion = models.CharField(max_length=255, blank=True, null=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.PositiveIntegerField(default=0)
    bloqueado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "credenciales"
        verbose_name = "Credencial"
        verbose_name_plural = "Credenciales"

    def __str__(self):
        return f"Credencial → {self.propietario}"

    def set_password(self, raw_password: str):
        self.contrasena_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.contrasena_hash)
