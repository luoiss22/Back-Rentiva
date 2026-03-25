from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase

from autenticacion.models import Propietario
from arrendatarios.models import Arrendatario
from propiedades.models import Propiedad
from .models import Contrato


class ContratoValidationTests(TestCase):
    """Tests de validaciones de negocio en contratos."""

    def setUp(self):
        self.propietario = Propietario.objects.create(
            nombre="Owner", apellidos="Test", email="owner@test.com",
        )
        self.propiedad = Propiedad.objects.create(
            propietario=self.propietario,
            nombre="Depa Centro",
            direccion="Av Reforma 100",
            ciudad="CDMX",
            estado_geografico="CDMX",
            tipo="departamento",
            costo_renta=15000,
        )
        self.arrendatario = Arrendatario.objects.create(
            nombre="Tenant", apellidos="Test",
        )

    def test_fecha_fin_mayor_que_inicio(self):
        contrato = Contrato(
            propiedad=self.propiedad,
            arrendatario=self.arrendatario,
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 1, 1),  # Anterior al inicio
            renta_acordada=15000,
            dia_pago=1,
            estado=Contrato.Estado.BORRADOR,
        )
        with self.assertRaises(ValidationError) as ctx:
            contrato.clean()
        self.assertIn("fecha_fin", ctx.exception.message_dict)

    def test_contrato_valido(self):
        contrato = Contrato(
            propiedad=self.propiedad,
            arrendatario=self.arrendatario,
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 12, 31),
            renta_acordada=15000,
            dia_pago=1,
            estado=Contrato.Estado.BORRADOR,
        )
        # No debe lanzar excepción
        contrato.clean()
