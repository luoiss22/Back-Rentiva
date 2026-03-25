import calendar
from datetime import date, timedelta
from contratos.models import Contrato
from pagos.models import Pago

def agregar_meses(fecha_origen, meses_a_sumar):
    mes = fecha_origen.month - 1 + meses_a_sumar
    anio = fecha_origen.year + mes // 12
    mes = mes % 12 + 1
    dia = min(fecha_origen.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)

def generar_pagos_pendientes(usuario):
    """
    Simula un crontab: Revisa los contratos activos del usuario (o todos si es admin)
    y genera los pagos devengados hasta el día de hoy, para mostrarse en /pagos/.
    También marca como vencidos los pagos pendientes cuya fecha límite ya pasó.
    """
    hoy = date.today()
    
    # --- ACTUALIZACIÓN DE PAGOS VENCIDOS ---
    # Marcamos como VENCIDO cualquier pago pendiente cuya fecha límite haya sido antes de hoy.
    pagos_a_vencer = Pago.objects.filter(
        estado=Pago.Estado.PENDIENTE,
        fecha_limite__lt=hoy
    )
    if getattr(usuario, "rol", None) != "admin" and usuario:
        pagos_a_vencer = pagos_a_vencer.filter(contrato__propiedad__propietario=usuario)
    
    pagos_a_vencer.update(estado=Pago.Estado.VENCIDO)
    # ---------------------------------------

    if getattr(usuario, "rol", None) == "admin":
        contratos_activos = Contrato.objects.filter(estado=Contrato.Estado.ACTIVO)
    else:
        contratos_activos = Contrato.objects.filter(propiedad__propietario=usuario, estado=Contrato.Estado.ACTIVO)

    for contrato in contratos_activos:
        if contrato.periodo_pago == Contrato.PeriodoPago.MENSUAL:
            # Empezamos en la fecha de inicio del contrato
            fecha_iter = contrato.fecha_inicio
            
            while fecha_iter <= hoy and fecha_iter <= contrato.fecha_fin:
                periodo_str = f"{fecha_iter.year}-{fecha_iter.month:02d}"
                
                # Definir fecha_limite asegurando que el día de pago no supere los días del mes actual
                try:
                    last_day = calendar.monthrange(fecha_iter.year, fecha_iter.month)[1]
                    day_to_use = min(contrato.dia_pago, last_day)
                    fecha_lim = date(fecha_iter.year, fecha_iter.month, day_to_use)
                except ValueError:
                    fecha_lim = fecha_iter
                
                # Crear el pago pendiente si no existe
                Pago.objects.get_or_create(
                    contrato=contrato,
                    periodo=periodo_str,
                    defaults={
                        'monto': contrato.renta_acordada,
                        'fecha_limite': fecha_lim,
                        'estado': Pago.Estado.PENDIENTE,
                    }
                )
                
                # Avanzar un mes
                fecha_iter = agregar_meses(fecha_iter, 1)

        elif contrato.periodo_pago == Contrato.PeriodoPago.DIARIO:
            fecha_iter = contrato.fecha_inicio
            while fecha_iter <= hoy and fecha_iter <= contrato.fecha_fin:
                periodo_str = fecha_iter.strftime("%Y-%m-%d")
                Pago.objects.get_or_create(
                    contrato=contrato,
                    periodo=periodo_str,
                    defaults={
                        'monto': contrato.renta_acordada,
                        'fecha_limite': fecha_iter,
                        'estado': Pago.Estado.PENDIENTE,
                    }
                )
                fecha_iter += timedelta(days=1)

        elif contrato.periodo_pago == Contrato.PeriodoPago.ANUAL:
            fecha_iter = contrato.fecha_inicio
            while fecha_iter <= hoy and fecha_iter <= contrato.fecha_fin:       
                periodo_str = f"{fecha_iter.year}"

                # Definir fecha_limite asegurando que el día de pago no supere los días del mes actual
                try:
                    last_day = calendar.monthrange(fecha_iter.year, fecha_iter.month)[1]
                    day_to_use = min(contrato.dia_pago, last_day)
                    fecha_lim = date(fecha_iter.year, fecha_iter.month, day_to_use)
                except ValueError:
                    fecha_lim = fecha_iter

                Pago.objects.get_or_create(
                    contrato=contrato,
                    periodo=periodo_str,
                    defaults={
                        'monto': contrato.renta_acordada,
                        'fecha_limite': fecha_lim,
                        'estado': Pago.Estado.PENDIENTE,
                    }
                )

                # Avanzar un año
                fecha_iter = agregar_meses(fecha_iter, 12)
