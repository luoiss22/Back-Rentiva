"""
Generación automática de notificaciones para pagos próximos a vencer,
pagos ya vencidos y contratos próximos a finalizar.

Se invoca desde NotificacionViewSet.list() de forma similar a como
pagos/utils.py genera los pagos pendientes.
"""

from datetime import date, timedelta
from django.utils import timezone

from autenticacion.models import Administrador
from contratos.models import Contrato
from pagos.models import Pago
from notificaciones.models import Notificacion


def generar_notificaciones_automaticas(usuario):
    """
    Revisa los contratos activos del usuario y genera notificaciones
    automáticas para:
    - Pagos que vencen en los próximos 3 días
    - Pagos que ya están vencidos
    - Contratos que finalizan en los próximos 30 días
    """
    hoy = date.today()
    ahora = timezone.now()

    if isinstance(usuario, Administrador):
        contratos = Contrato.objects.filter(estado=Contrato.Estado.ACTIVO)
    else:
        contratos = Contrato.objects.filter(
            propiedad__propietario=usuario,
            estado=Contrato.Estado.ACTIVO,
        )

    for contrato in contratos:
        # ── Pagos próximos a vencer (3 días) ──
        pagos_proximos = Pago.objects.filter(
            contrato=contrato,
            estado=Pago.Estado.PENDIENTE,
            fecha_limite__gte=hoy,
            fecha_limite__lte=hoy + timedelta(days=3),
        )
        for pago in pagos_proximos:
            tipo = Notificacion.TipoNotificacion.PAGO_PROXIMO
            titulo = f"Pago próximo: {pago.periodo}"
            _crear_si_no_existe(
                contrato=contrato,
                tipo=tipo,
                titulo=titulo,
                mensaje=(
                    f"El pago del periodo {pago.periodo} por ${pago.monto} "
                    f"vence el {pago.fecha_limite}."
                ),
                fecha_programada=ahora,
            )

        # ── Pagos vencidos sin notificación ──
        pagos_vencidos = Pago.objects.filter(
            contrato=contrato,
            estado=Pago.Estado.VENCIDO,
        )
        for pago in pagos_vencidos:
            tipo = Notificacion.TipoNotificacion.PAGO_VENCIDO
            titulo = f"Pago vencido: {pago.periodo}"
            _crear_si_no_existe(
                contrato=contrato,
                tipo=tipo,
                titulo=titulo,
                mensaje=(
                    f"El pago del periodo {pago.periodo} por ${pago.monto} "
                    f"venció el {pago.fecha_limite} y no ha sido cubierto."
                ),
                fecha_programada=ahora,
            )

        # ── Contrato próximo a vencer (30 días) ──
        dias_restantes = (contrato.fecha_fin - hoy).days
        if 0 < dias_restantes <= 30:
            tipo = Notificacion.TipoNotificacion.CONTRATO_VENCER
            titulo = f"Contrato por vencer en {dias_restantes} días"
            _crear_si_no_existe(
                contrato=contrato,
                tipo=tipo,
                titulo=titulo,
                mensaje=(
                    f"El contrato de {contrato.propiedad.nombre} con "
                    f"{contrato.arrendatario} finaliza el {contrato.fecha_fin}."
                ),
                fecha_programada=ahora,
            )


def _crear_si_no_existe(contrato, tipo, titulo, mensaje, fecha_programada):
    """
    Crea la notificación solo si no existe otra con el mismo contrato,
    tipo y titulo. Así evitamos duplicados cada vez que se lista.
    """
    existe = Notificacion.objects.filter(
        contrato=contrato,
        tipo=tipo,
        titulo=titulo,
    ).exists()
    if not existe:
        Notificacion.objects.create(
            contrato=contrato,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            fecha_programada=fecha_programada,
        )
