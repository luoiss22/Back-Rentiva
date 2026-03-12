from django.db import models


class Propiedad(models.Model):
    """Inmueble disponible para renta."""

    class TipoPropiedad(models.TextChoices):
        CASA = "casa", "Casa"
        DEPARTAMENTO = "departamento", "Departamento"
        LOCAL = "local", "Local comercial"
        OFICINA = "oficina", "Oficina"
        TERRENO = "terreno", "Terreno"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        RENTADA = "rentada", "Rentada"
        MANTENIMIENTO = "mantenimiento", "En mantenimiento"
        INACTIVA = "inactiva", "Inactiva"

    propietario = models.ForeignKey(
        "autenticacion.Propietario",
        on_delete=models.CASCADE,
        related_name="propiedades",
    )
    nombre = models.CharField(max_length=200)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=120)
    estado_geografico = models.CharField(max_length=120)
    codigo_postal = models.CharField(max_length=5, blank=True)
    tipo = models.CharField(max_length=20, choices=TipoPropiedad.choices)
    descripcion = models.TextField(blank=True)
    costo_renta = models.DecimalField(max_digits=12, decimal_places=2)
    superficie_m2 = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "propiedades"
        ordering = ["-created_at"]
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"

    def __str__(self):
        return f"{self.nombre} — {self.ciudad}"


class PropiedadDetalle(models.Model):
    """Detalles dinámicos de la propiedad (clave → valor)."""

    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    clave = models.CharField(max_length=100)
    valor = models.CharField(max_length=255)

    class Meta:
        db_table = "propiedad_detalles"
        verbose_name = "Detalle de propiedad"
        verbose_name_plural = "Detalles de propiedad"
        unique_together = ("propiedad", "clave")

    def __str__(self):
        return f"{self.clave}: {self.valor}"


class Mobiliario(models.Model):
    """Catálogo general de mobiliario / equipamiento."""

    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100, blank=True)
    descripcion = models.TextField(blank=True)
    foto = models.ImageField(upload_to="mobiliario/fotos/", blank=True, null=True)

    class Meta:
        db_table = "mobiliario"
        ordering = ["nombre"]
        verbose_name = "Mobiliario"
        verbose_name_plural = "Mobiliario"

    def __str__(self):
        return self.nombre


class PropiedadMobiliario(models.Model):
    """Relación propiedad ↔ mobiliario con metadatos."""

    class Estado(models.TextChoices):
        BUENO = "bueno", "Bueno"
        REGULAR = "regular", "Regular"
        MALO = "malo", "Malo"
        REPARACION = "reparacion", "En reparación"

    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name="mobiliarios",
    )
    mobiliario = models.ForeignKey(
        Mobiliario,
        on_delete=models.CASCADE,
        related_name="propiedades",
    )
    cantidad = models.PositiveIntegerField(default=1)
    valor_estimado = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.BUENO,
    )

    class Meta:
        db_table = "propiedad_mobiliario"
        verbose_name = "Mobiliario de propiedad"
        verbose_name_plural = "Mobiliario de propiedades"
        unique_together = ("propiedad", "mobiliario")

    def __str__(self):
        return f"{self.mobiliario} × {self.cantidad} → {self.propiedad}"


class FotoPropiedad(models.Model):
    """Galería de fotos de una propiedad."""

    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name="fotos",
    )
    imagen = models.ImageField(upload_to="propiedades/fotos/")
    descripcion = models.CharField(max_length=255, blank=True)
    es_principal = models.BooleanField(
        default=False,
        help_text="Marca esta foto como imagen principal de la propiedad",
    )
    orden = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "propiedad_fotos"
        ordering = ["orden", "-es_principal"]
        verbose_name = "Foto de propiedad"
        verbose_name_plural = "Fotos de propiedad"

    def __str__(self):
        return f"Foto de {self.propiedad} ({'principal' if self.es_principal else self.orden})"

    def save(self, *args, **kwargs):
        # Si esta foto se marca como principal, desmarcar las demás
        if self.es_principal:
            FotoPropiedad.objects.filter(
                propiedad=self.propiedad, es_principal=True,
            ).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)
