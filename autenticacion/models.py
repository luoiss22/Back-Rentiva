from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Propietario(models.Model):
    """Propietario / arrendador de inmuebles."""

    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        PROPIETARIO = "propietario", "Propietario"

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
    foto = models.ImageField(upload_to="propietarios/fotos/", blank=True, null=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.PROPIETARIO)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
