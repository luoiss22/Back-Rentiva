import calendar
from datetime import date, timedelta

from django.test import TestCase

from autenticacion.models import Propietario
from arrendatarios.models import Arrendatario
from contratos.models import Contrato
from pagos.models import Pago
from pagos.utils import generar_pagos_pendientes
from propiedades.models import Propiedad


class PagosGenerationTests(TestCase):
	def setUp(self):
		self.propietario = Propietario.objects.create(
			nombre="Owner", apellidos="Test", email="owner-pagos@test.com",
		)
		self.propiedad = Propiedad.objects.create(
			propietario=self.propietario,
			nombre="Casa Pagos",
			direccion="Calle 1",
			ciudad="CDMX",
			estado_geografico="CDMX",
			tipo="casa",
			costo_renta=12000,
		)
		self.arrendatario = Arrendatario.objects.create(
			nombre="Tenant", apellidos="Pagos",
		)

	def test_primer_periodo_no_queda_vencido_antes_de_inicio(self):
		hoy = date.today()
		if hoy.day >= 15:
			inicio = date(hoy.year, hoy.month, 15)
		else:
			ultimo_mes_anterior = hoy.replace(day=1) - timedelta(days=1)
			inicio = date(ultimo_mes_anterior.year, ultimo_mes_anterior.month, 15)

		contrato = Contrato.objects.create(
			propiedad=self.propiedad,
			arrendatario=self.arrendatario,
			fecha_inicio=inicio,
			fecha_fin=hoy + timedelta(days=180),
			renta_acordada=12000,
			dia_pago=1,
			periodo_pago=Contrato.PeriodoPago.MENSUAL,
			estado=Contrato.Estado.ACTIVO,
		)

		generar_pagos_pendientes(self.propietario)

		periodo_inicio = f"{inicio.year}-{inicio.month:02d}"
		pago = Pago.objects.get(contrato=contrato, periodo=periodo_inicio)
		self.assertEqual(pago.fecha_limite, inicio)

	def test_actualiza_fecha_limite_si_cambia_dia_pago_en_no_liquidados(self):
		hoy = date.today()
		inicio = date(hoy.year, hoy.month, 1)

		contrato = Contrato.objects.create(
			propiedad=self.propiedad,
			arrendatario=self.arrendatario,
			fecha_inicio=inicio,
			fecha_fin=hoy + timedelta(days=180),
			renta_acordada=12000,
			dia_pago=5,
			periodo_pago=Contrato.PeriodoPago.MENSUAL,
			estado=Contrato.Estado.ACTIVO,
		)

		generar_pagos_pendientes(self.propietario)

		periodo_actual = f"{hoy.year}-{hoy.month:02d}"
		pago = Pago.objects.get(contrato=contrato, periodo=periodo_actual)
		self.assertEqual(pago.fecha_limite.day, 5)

		contrato.dia_pago = 20
		contrato.save(update_fields=["dia_pago"])
		generar_pagos_pendientes(self.propietario)

		pago.refresh_from_db()
		esperado = min(20, calendar.monthrange(hoy.year, hoy.month)[1])
		self.assertEqual(pago.fecha_limite.day, esperado)
