import calendar
from datetime import date, timedelta
from decimal import Decimal
from autenticacion.models import Administrador
from contratos.models import Contrato
from pagos.models import Pago

def agregar_meses(fecha_origen, meses_a_sumar):
    mes = fecha_origen.month - 1 + meses_a_sumar
    anio = fecha_origen.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha_origen.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)


def _calcular_renta_con_incremento(contrato, fecha_periodo):
    """
    Aplica el incremento anual compuesto sobre la renta acordada.
    Por cada año completo transcurrido desde el inicio del contrato,
    se aplica el porcentaje de incremento_anual.
    Ejemplo: renta=10000, incremento_anual=5%, fecha_inicio=2024-01-01
    - 2024: 10000
    - 2025: 10500  (10000 * 1.05)
    - 2026: 11025  (10000 * 1.05^2)
    """
    if not contrato.incremento_anual or contrato.incremento_anual == 0:
        return contrato.renta_acordada

    anios_transcurridos = fecha_periodo.year - contrato.fecha_inicio.year
    if anios_transcurridos <= 0:
        return contrato.renta_acordada

    factor = (1 + contrato.incremento_anual / Decimal('100')) ** anios_transcurridos
    return (contrato.renta_acordada * factor).quantize(Decimal('0.01'))

def generar_pagos_pendientes(usuario):
    """
    Simula un crontab: Revisa los contratos activos del usuario (o todos si es admin)
    y genera los pagos devengados hasta el día de hoy, para mostrarse en /pagos/.
    También marca como vencidos los pagos pendientes cuya fecha límite ya pasó.
    Aplica el incremento anual de renta cuando corresponde.
    """
    hoy = date.today()
    
    # --- ACTUALIZACIÓN DE PAGOS VENCIDOS ---
    pagos_a_vencer = Pago.objects.filter(
        estado=Pago.Estado.PENDIENTE,
        fecha_limite__lt=hoy
    )
    if not isinstance(usuario, Administrador) and usuario:
        pagos_a_vencer = pagos_a_vencer.filter(contrato__propiedad__propietario=usuario)
    
    pagos_a_vencer.update(estado=Pago.Estado.VENCIDO)
    # ---------------------------------------

    if isinstance(usuario, Administrador):
        contratos_activos = Contrato.objects.filter(estado=Contrato.Estado.ACTIVO)
    else:
        contratos_activos = Contrato.objects.filter(propiedad__propietario=usuario, estado=Contrato.Estado.ACTIVO)

    def _upsert_pago_no_liquidado(contrato, periodo_str, monto, fecha_lim):
        pago, creado = Pago.objects.get_or_create(
            contrato=contrato,
            periodo=periodo_str,
            defaults={
                'monto': monto,
                'fecha_limite': fecha_lim,
                'estado': Pago.Estado.PENDIENTE,
            }
        )

        # Si ya existe y no está liquidado, sincronizar monto/fecha límite ante cambios de contrato.
        if not creado and pago.estado != Pago.Estado.PAGADO:
            cambios = False
            if pago.monto != monto:
                pago.monto = monto
                cambios = True
            if pago.fecha_limite != fecha_lim:
                pago.fecha_limite = fecha_lim
                cambios = True
            if cambios:
                pago.save()

    for contrato in contratos_activos:
        if contrato.periodo_pago == Contrato.PeriodoPago.MENSUAL:
            fecha_iter = contrato.fecha_inicio
            es_primer_periodo = True
            
            while fecha_iter <= hoy and fecha_iter <= contrato.fecha_fin:
                periodo_str = f"{fecha_iter.year}-{fecha_iter.month:02d}"
                
                try:
                    last_day = calendar.monthrange(fecha_iter.year, fecha_iter.month)[1]
                    day_to_use = min(contrato.dia_pago, last_day)
                    fecha_lim = date(fecha_iter.year, fecha_iter.month, day_to_use)
                    # Si el contrato inicia a mitad de periodo, no crear un vencimiento anterior al inicio.
                    if es_primer_periodo and fecha_lim < contrato.fecha_inicio:
                        fecha_lim = contrato.fecha_inicio
                except ValueError:
                    fecha_lim = fecha_iter
                
                monto = _calcular_renta_con_incremento(contrato, fecha_iter)

                _upsert_pago_no_liquidado(contrato, periodo_str, monto, fecha_lim)
                
                fecha_iter = agregar_meses(fecha_iter, 1)
                es_primer_periodo = False

        elif contrato.periodo_pago == Contrato.PeriodoPago.DIARIO:
            fecha_iter = contrato.fecha_inicio
            while fecha_iter <= hoy and fecha_iter <= contrato.fecha_fin:
                periodo_str = fecha_iter.strftime("%Y-%m-%d")
                monto = _calcular_renta_con_incremento(contrato, fecha_iter)

                _upsert_pago_no_liquidado(contrato, periodo_str, monto, fecha_iter)
                fecha_iter += timedelta(days=1)

        elif contrato.periodo_pago == Contrato.PeriodoPago.ANUAL:
            fecha_iter = contrato.fecha_inicio
            es_primer_periodo = True
            while fecha_iter <= hoy and fecha_iter <= contrato.fecha_fin:       
                periodo_str = f"{fecha_iter.year}"

                try:
                    last_day = calendar.monthrange(fecha_iter.year, fecha_iter.month)[1]
                    day_to_use = min(contrato.dia_pago, last_day)
                    fecha_lim = date(fecha_iter.year, fecha_iter.month, day_to_use)
                    if es_primer_periodo and fecha_lim < contrato.fecha_inicio:
                        fecha_lim = contrato.fecha_inicio
                except ValueError:
                    fecha_lim = fecha_iter

                monto = _calcular_renta_con_incremento(contrato, fecha_iter)

                _upsert_pago_no_liquidado(contrato, periodo_str, monto, fecha_lim)

                fecha_iter = agregar_meses(fecha_iter, 12)
                es_primer_periodo = False
