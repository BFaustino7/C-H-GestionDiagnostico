from django.shortcuts import render, get_object_or_404
from .models import OrdenReparacion, FichaTecnica, Cliente, Equipo, Producto
import random
from datetime import datetime, timedelta
#-----------------------------------------------------#
from django.shortcuts import render, redirect
from django.db import transaction
from .forms import ClienteForm, EquipoForm, OrdenIngresoForm
#-----------------------------------------------------#
from django.db.models import Q # Para búsquedas complejas


def ingreso_equipo(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        equipo_form = EquipoForm(request.POST)
        orden_form = OrdenIngresoForm(request.POST)

        # Validar que todos los formularios tengan datos correctos
        if cliente_form.is_valid() and equipo_form.is_valid() and orden_form.is_valid():
            try:
                # Iniciar transacción atómica
                with transaction.atomic():
                    
                    # 1. Guardar el Cliente
                    cliente = cliente_form.save()

                    # 2. Guardar el Equipo y asociarlo al Cliente
                    equipo = equipo_form.save(commit=False)
                    equipo.cliente = cliente
                    equipo.save()

                    # 3. Generar la Ficha Técnica en blanco asociada al Equipo
                    FichaTecnica.objects.create(
                        equipo=equipo,
                        gas_tipo='',
                        gas_cantidad=0,
                        datos_electricos=''
                    )

                    # 4. Crear la Orden de Reparación asociada al Equipo
                    orden = orden_form.save(commit=False)
                    orden.equipo = equipo
                    # Nota: El estado por defecto ya es 'PENDIENTE' y pago 'DEBE' en tu modelo
                    orden.save()

                # Redirigir al usuario tras un ingreso exitoso (ajustar 'tablero' según tu urls.py)
                return redirect('tablero') 
            
            except Exception as e:
                # Agregar mensajes de error de Django (messages.error)
                pass
    else:
        # Cargar formularios vacíos si la petición es GET
        cliente_form = ClienteForm()
        equipo_form = EquipoForm()
        orden_form = OrdenIngresoForm()

    context = {
        'cliente_form': cliente_form,
        'equipo_form': equipo_form,
        'orden_form': orden_form
    }
    
    return render(request, 'gestion/ingreso_equipo.html', context)

def tablero_principal(request):
    # 1. CONSULTAS BD
    ordenes_taller = OrdenReparacion.objects.filter(
        estado__in=['PENDIENTE', 'DIAGNOSTICO', 'ESPERA', 'REPARACION']
    ).order_by('-fecha_ingreso')

    ordenes_para_entregar = OrdenReparacion.objects.filter(estado='TERMINADO').order_by('-fecha_ingreso')
    ordenes_entregadas = OrdenReparacion.objects.filter(estado='ENTREGADO').order_by('-fecha_ingreso')[:5]

    # 2. GENERACIÓN DE DATOS IOT
    banco_pruebas = []
    
    equipos_en_banco = ordenes_taller.filter(estado='REPARACION')
    if not equipos_en_banco:
        equipos_en_banco = ordenes_taller.filter(estado='DIAGNOSTICO')

    for orden in equipos_en_banco:
        # Generamos historial de 10 puntos
        # Simulamos R410a: Presión 115-125 PSI
        historial_presion_baja = []
        historial_temp = []
        historial_superheat = []
        historial_amp = []
        historial_watts = []
        historial_alta = []

        for _ in range(10):
            # A. Generar Presión Baja (PSI)
            p_baja = round(random.uniform(115, 125), 1)
            historial_presion_baja.append(p_baja)

            # B. Calcular Temp. Saturación (Aprox R410a: 118PSI ~= 4°C)
            # Fórmula linealizada simple para simulación: (PSI - 100) * 0.2
            t_sat = (p_baja - 100) * 0.2 + 2 
            
            # C. Generar Superheat (Ideal entre 5K y 8K)
            sh_simulado = round(random.uniform(4.0, 9.0), 1)
            historial_superheat.append(sh_simulado)

            # D. Temp. Retorno (Lo que mide la sonda) = T_sat + Superheat
            t_retorno = round(t_sat + sh_simulado, 1)
            historial_temp.append(t_retorno)

            # E. Parte Eléctrica/Mecánica
            amp = round(random.uniform(3.5, 4.2), 1)
            historial_amp.append(amp)
            
            voltaje = random.randint(218, 223)
            historial_watts.append(int(voltaje * amp))
            
            # Alta Presión (aprox 3.2x de la baja en trabajo normal)
            historial_alta.append(int(p_baja * 3.2))

        ahora = datetime.now()
        labels = [(ahora - timedelta(minutes=i)).strftime("%H:%M") for i in range(10, 0, -1)]

        banco_pruebas.append({
            'id': orden.id,
            'equipo_marca': f"{orden.equipo.marca} {orden.equipo.modelo}",
            
            # VALORES ACTUALES (Para los displays PLC)
            'baja_presion': int(historial_presion_baja[-1]),
            'alta_presion': int(historial_alta[-1]),
            'temperatura': historial_temp[-1],
            'superheat': historial_superheat[-1],
            'potencia': historial_watts[-1],
            
            # LISTAS PARA GRÁFICOS (Para los scripts de Chart.js)
            'baja_presion_data': historial_presion_baja,
            'alta_presion_data': historial_alta,
            'temperatura_data': historial_temp,
            'superheat_data': historial_superheat,
            'potencia_data': historial_watts,
            'labels': labels,
        })

    return render(request, 'gestion/tablero.html', {
        'ordenes_en_proceso': ordenes_taller, 
        'ordenes_para_entregar': ordenes_para_entregar,
        'ordenes_entregadas': ordenes_entregadas,
        'banco_pruebas': banco_pruebas,
    })

# --- VISTAS SECUNDARIAS ---

def imprimir_remito(request, orden_id):
    orden = get_object_or_404(OrdenReparacion, pk=orden_id)
    return render(request, 'gestion/remito_imprimible.html', {'orden': orden})

def detalle_orden(request, orden_id):
    # 1. Intentamos obtener la orden (Tu lógica de control)
    try:
        orden = OrdenReparacion.objects.get(pk=orden_id)
    except OrdenReparacion.DoesNotExist:
        return render(request, 'gestion/orden_no_encontrada.html', {'id_buscado': orden_id})
    
    # 2. Lógica para procesar el formulario (Lo nuevo)
    if request.method == 'POST':
        orden.diagnostico_tecnico = request.POST.get('diagnostico')
        orden.costo_mano_obra = request.POST.get('mano_obra')
        orden.estado = request.POST.get('estado')
        orden.save()
        # Redirigimos para "limpiar" el envío del formulario y ver los cambios
        return redirect('detalle_orden', orden_id=orden.id)

    # 3. Renderizado normal (GET)
    return render(request, 'gestion/detalle_orden.html', {'orden': orden})


def lista_clientes(request):
    busqueda = request.GET.get('buscar')
    if busqueda:
        # Busca por nombre o teléfono
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=busqueda) | Q(telefono__icontains=busqueda)
        )
    else:
        clientes = Cliente.objects.all().order_by('nombre')
    
    return render(request, 'gestion/lista_clientes.html', {'lista_clientes': clientes})

def lista_equipos(request):
    # Traemos los equipos con su cliente relacionado para no saturar la DB (select_related)
    equipos = Equipo.objects.select_related('cliente').all()
    
    return render(request, 'gestion/lista_equipos.html', {'lista_equipos': equipos})

def calendario_taller(request):
    # Mostramos órdenes pendientes y en reparación para organizar la semana
    proximos_trabajos = OrdenReparacion.objects.filter(
        estado__in=['PENDIENTE', 'DIAGNOSTICO', 'REPARACION']
    ).order_by('fecha_ingreso')
    
    return render(request, 'gestion/calendario.html', {
        'ordenes': proximos_trabajos,
        'hoy': datetime.now()
    })

def configuracion_sistema(request):
    productos = Producto.objects.all()
    return render(request, 'gestion/configuracion.html', {'productos': productos})

from django.shortcuts import render, get_object_or_404
from .models import Equipo, OrdenReparacion

def historial_equipo(request, equipo_id):
    # Buscamos el equipo o tiramos 404 si no existe
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Traemos todas sus órdenes, de la más nueva a la más vieja
    ordenes = OrdenReparacion.objects.filter(equipo=equipo).order_by('-fecha_ingreso')
    
    context = {
        'equipo': equipo,
        'ordenes': ordenes,
    }
    
    return render(request, 'gestion/historial_equipo.html', context)