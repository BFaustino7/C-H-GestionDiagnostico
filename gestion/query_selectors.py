from django.db.models import Q, Max, F
from django.utils import timezone
from .models import OrdenReparacion, Cliente, Equipo, Producto

def get_equipos_con_stats(tipo_filtro=None):
    # Usamos annotate para traer la fecha de la última orden de cada equipo en una sola consulta
    base = Equipo.objects.select_related('cliente').prefetch_related('ficha').annotate(
        fecha_ultimo_service=Max('ordenreparacion__fecha_ingreso')
    ).all()
    
    ahora = timezone.now()
    
    # Cálculos de Service (Basado en los 90 días que definiste en el HTML)
    # Un equipo está "OK" si tuvo service hace menos de 90 días
    limite_ok = ahora - timezone.timedelta(days=90)
    
    counts = {
        'count_total': base.count(),
        'count_split': base.filter(tipo='SPLIT').count(),
        'count_heladera': base.filter(Q(tipo='HELADERA') | Q(tipo='COMERCIAL')).count(),
        'count_lavarropas': base.filter(tipo='LAVARROPAS').count(),
        'count_camara': base.filter(tipo='CAMARA').count(), # Agregado
        'equipos_ok': base.filter(fecha_ultimo_service__gte=limite_ok).count(), # Agregado
        'equipos_pendientes': base.filter(
            Q(fecha_ultimo_service__lt=limite_ok) | Q(fecha_ultimo_service__isnull=True)
        ).count(), # Agregado
    }

    # Filtrado lógico
    if tipo_filtro:
        tipo_upper = tipo_filtro.upper()
        # Mapeo de 'camara' del HTML al 'COMERCIAL' o 'CAMARA' del modelo
        if tipo_upper == 'HELADERA':
            base = base.filter(Q(tipo='HELADERA') | Q(tipo='COMERCIAL'))
        elif tipo_upper == 'CAMARA':
            # Si en tu modelo usás COMERCIAL para las cámaras, ajustá esto:
            base = base.filter(tipo='CAMARA') 
        else:
            base = base.filter(tipo=tipo_upper)
            
    return base, counts
    
def get_ordenes_tablero():
    return OrdenReparacion.objects.filter(
        estado__in=['PENDIENTE', 'DIAGNOSTICO', 'ESPERA', 'REPARACION']
    ).order_by('-fecha_ingreso')

def get_ordenes_para_entregar():
    # Corregido: Usamos 'TERMINADO' que es el valor de tu Model
    return OrdenReparacion.objects.filter(estado='COMPLETADO').order_by('-fecha_ingreso')

def get_ordenes_recientes_entregadas(limite=5):
    return OrdenReparacion.objects.filter(estado='ENTREGADO').order_by('-fecha_ingreso')[:limite]

def buscar_clientes(query=None):
    """Buscador omnicanal: filtra por nombre, tel, dirección o email."""
    clientes = Cliente.objects.all().order_by('nombre')
    
    if query:
        # icontains busca coincidencias parciales sin importar mayúsculas/minúsculas
        clientes = clientes.filter(
            Q(nombre__icontains=query) | 
            Q(telefono__icontains=query) |
            Q(direccion__icontains=query) |
            Q(email__icontains=query)
        ).distinct() # El distinct evita duplicados si el texto coincide en dos campos
        
    return clientes

def get_equipos_con_stats(tipo_filtro=None):
    base = Equipo.objects.select_related('cliente').prefetch_related('ficha').all()
    
    # Contadores
    counts = {
        'count_total': base.count(),
        'count_split': base.filter(tipo='SPLIT').count(),
        'count_heladera': base.filter(Q(tipo='HELADERA') | Q(tipo='COMERCIAL')).count(),
        'count_lavarropas': base.filter(tipo='LAVARROPAS').count(),
    }

    # Filtrado
    if tipo_filtro:
        tipo_upper = tipo_filtro.upper()
        if tipo_upper == 'HELADERA':
            base = base.filter(Q(tipo='HELADERA') | Q(tipo='COMERCIAL'))
        else:
            base = base.filter(tipo=tipo_upper)
            
    return base, counts

def get_historial_equipo(equipo_id):
    return OrdenReparacion.objects.filter(equipo_id=equipo_id).order_by('-fecha_ingreso')