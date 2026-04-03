import calendar
from collections import defaultdict
from datetime import datetime, timedelta
from django.db import transaction
from .models import FichaTecnica, Producto, DetalleInsumo, OrdenReparacion, EventoCalendario

@transaction.atomic
def registrar_nuevo_ingreso(cliente_form, equipo_form, orden_form):
    """Encapsula la creación atómica de Cliente -> Equipo -> Ficha -> Orden"""
    cliente = cliente_form.save()

    equipo = equipo_form.save(commit=False)
    equipo.cliente = cliente
    equipo.save()

    # Crear ficha técnica inicial
    FichaTecnica.objects.create(equipo=equipo)

    orden = orden_form.save(commit=False)
    orden.equipo = equipo
    orden.save()
    return orden

@transaction.atomic
def procesar_insumos_orden(orden, insumos_data):
    for insumo in insumos_data:
        nombre = insumo.get('nombre')
        precio = insumo.get('precio')
        
        prod, _ = Producto.objects.get_or_create(
            nombre=nombre,
            defaults={'precio_venta': precio, 'precio_compra': 0, 'stock': 0}
        )
        DetalleInsumo.objects.create(
            orden=orden, producto=prod, cantidad=1, precio_congelado=precio
        )

def actualizar_cliente(cliente_instance, form_data):
    """Procesa la actualización de datos de un cliente existente."""
    from .forms import ClienteForm
    form = ClienteForm(form_data, instance=cliente_instance)
    if form.is_valid():
        return form.save()
    return None

# Si tenés la función guardar_detalle_orden que armamos hace un rato, dejala acá también.


# =====================================================================
# SERVICIO DE CALENDARIO (Refactorizado y Limpio)
# =====================================================================

class ServicioCalendario:
    MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    @classmethod
    def generar_contexto(cls, anio, mes):
        # Usamos .date() para comparar solo fechas, evitando problemas de horas
        hoy_dt = datetime.now()
        hoy_date = hoy_dt.date()
        
        # 1. Fechas límite basadas en el mes/año QUE RECIBE la función
        _, ultimo_dia = calendar.monthrange(anio, mes)
        fecha_inicio = datetime(anio, mes, 1, 0, 0, 0)
        fecha_fin = datetime(anio, mes, ultimo_dia, 23, 59, 59)
        
        # 2. Consultar BD (El __range es vital para MSSQL)
        eventos = EventoCalendario.objects.filter(fecha_hora__range=(fecha_inicio, fecha_fin))
        ordenes = OrdenReparacion.objects.filter(fecha_ingreso__range=(fecha_inicio, fecha_fin), estado__in=['PENDIENTE', 'DIAGNOSTICO'])

        # 3. Agrupar con defaultdict
        eventos_por_dia = defaultdict(lambda: defaultdict(list))
        
        for ev in eventos:
            # Importante: usar .date().day para asegurar que el día sea el correcto tras la conversión de zona horaria
            dia = ev.fecha_hora.date().day 
            eventos_por_dia[dia][ev.tipo].append({
                'hora': ev.fecha_hora.strftime('%H:%M'), 
                'descripcion': ev.titulo
            })
            
        for orden in ordenes:
            dia = orden.fecha_ingreso.date().day
            eventos_por_dia[dia]['TURNO'].append({
                'hora': orden.fecha_ingreso.strftime('%H:%M'), 
                'descripcion': f"Ingreso: {orden.equipo.cliente.nombre}"
            })

        # 4. Construir la grilla
        cal = calendar.Calendar(firstweekday=0)
        dias_del_mes, dias_vacios_inicio, dias_vacios_fin = [], [], []
        total_eventos = 0

        # Iteramos los días del mes (0 para vacíos, 1-31 para días reales)
        for dia_num in cal.itermonthdays(anio, mes):
            if dia_num == 0:
                if not dias_del_mes:
                    dias_vacios_inicio.append(1)
                else:
                    dias_vacios_fin.append(1)
            else:
                # Creamos un objeto date para este día específico
                fecha_actual = datetime(anio, mes, dia_num).date()
                eventos_hoy = eventos_por_dia[dia_num]
                
                dias_del_mes.append({
                    'numero': dia_num,
                    'es_hoy': (fecha_actual == hoy_date),
                    'es_fin_de_semana': fecha_actual.weekday() in (5, 6), # 5=Sábado, 6=Domingo
                    'turnos': eventos_hoy['TURNO'],
                    'entregas': eventos_hoy['ENTREGA'],
                    'alertas': eventos_hoy['ALERTA'],
                    'mas_eventos': 0
                })
                total_eventos += sum(len(lista) for lista in eventos_hoy.values())

        # 5. Estadísticas y Navegación (lo mismo que tenías)
        stats = {
            'total_turnos': sum(len(d['TURNO']) for d in eventos_por_dia.values()),
            'total_entregas': sum(len(d['ENTREGA']) for d in eventos_por_dia.values()),
            'total_alertas': sum(len(d['ALERTA']) for d in eventos_por_dia.values()),
        }

        mes_sig, anio_sig = (1, anio + 1) if mes == 12 else (mes + 1, anio)
        mes_ant, anio_ant = (12, anio - 1) if mes == 1 else (mes - 1, anio)

        return {
            'nombre_mes': cls.MESES[mes],
            'anio_actual': anio,
            'mes_siguiente': mes_sig, 'anio_siguiente': anio_sig,
            'mes_anterior': mes_ant, 'anio_anterior': anio_ant,
            'dias_vacios_inicio': dias_vacios_inicio,
            'dias_del_mes': dias_del_mes,
            'dias_vacios_fin': dias_vacios_fin,
            'total_eventos_mes': total_eventos,
            'hoy_numero': hoy_dt.day,
            'hoy_nombre_dia': cls.DIAS[hoy_dt.weekday()],
            'hoy_mes_anio': f"{cls.MESES[hoy_dt.month]} {hoy_dt.year}",
            'stats_mes': stats
        }