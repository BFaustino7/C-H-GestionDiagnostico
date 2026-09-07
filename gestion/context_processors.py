"""Context processors globales del proyecto C&H GestiónDiagnostico."""


def site_stats(request):
    """Expone métricas del sistema a todos los templates (contrato del sidebar)."""
    from .models import Alarma

    return {
        'alarmas_activas_count': Alarma.objects.filter(atendida=False).count(),
    }