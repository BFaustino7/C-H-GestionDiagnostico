import json
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime

# --- MODELOS Y FORMULARIOS ---
from .models import OrdenReparacion, Equipo, FichaTecnica, Producto, Cliente
from .forms import (ClienteForm, EquipoForm, OrdenIngresoForm, 
                    OrdenTecnicaForm, EspecificacionesForm, EventoCalendarioForm)

# --- CAPAS DE ABSTRACCIÓN (MODULARIZACIÓN) ---
from . import query_selectors as sel  # Nombre corregido
from . import services as svc

from iot.iot_simulador import generar_datos_banco_pruebas
from .services import ServicioCalendario
from .utils import api_success, api_error

def tablero_principal(request):
    ordenes_taller = sel.get_ordenes_tablero()
    equipos_monitoreo = ordenes_taller.filter(estado='REPARACION') or ordenes_taller.filter(estado='DIAGNOSTICO')

    return render(request, 'gestion/tablero.html', {
        'ordenes_en_proceso': ordenes_taller,
        'ordenes_para_entregar': sel.get_ordenes_para_entregar(),
        'ordenes_entregadas': sel.get_ordenes_recientes_entregadas(),
        'banco_pruebas': generar_datos_banco_pruebas(equipos_monitoreo),
    })

def ingreso_equipo(request):
    if request.method == 'POST':
        c_form, e_form, o_form = ClienteForm(request.POST), EquipoForm(request.POST), OrdenIngresoForm(request.POST)
        if c_form.is_valid() and e_form.is_valid() and o_form.is_valid():
            svc.registrar_nuevo_ingreso(c_form, e_form, o_form)
            return redirect('tablero')
    else:
        c_form, e_form, o_form = ClienteForm(), EquipoForm(), OrdenIngresoForm()

    return render(request, 'gestion/ingreso_equipo.html', {
        'cliente_form': c_form, 'equipo_form': e_form, 'orden_form': o_form
    })

def detalle_orden(request, orden_id):
    orden = get_object_or_404(OrdenReparacion, pk=orden_id)
    equipo = orden.equipo
    ficha, _ = FichaTecnica.objects.get_or_create(equipo=equipo)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Delegamos toda la lógica pesada a services.py
            exito, errores = svc.guardar_detalle_orden(orden, ficha, equipo, data)
            
            if exito:
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'errors': errores}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # Si es GET, renderizamos el template con los formularios vacíos/instanciados
    return render(request, 'gestion/detalle_orden.html', {
        'orden': orden,
        'form_orden': OrdenTecnicaForm(instance=orden),
        'form_ficha': EspecificacionesForm(instance=ficha),
        'form_equipo': EquipoForm(instance=equipo),
        'total_general': orden.total_calculado
    })

def imprimir_remito(request, orden_id):
    orden = get_object_or_404(OrdenReparacion, pk=orden_id)
    return render(request, 'gestion/remito_imprimible.html', {'orden': orden})

def lista_clientes(request):
    query = request.GET.get('q', '')   
    clientes = sel.buscar_clientes(query)
    
    return render(request, 'gestion/lista_clientes.html', {
        'lista_clientes': clientes,
        'busqueda': query,
        'total_clientes': clientes.count()
    })

def lista_equipos(request):
    tipo = request.GET.get('tipo')
    equipos_list, counts = sel.get_equipos_con_stats(tipo)
    
    # --- Lógica de Paginación ---
    paginator = Paginator(equipos_list, 12) # 12 equipos por página
    page_number = request.GET.get('page')
    equipos_paginados = paginator.get_page(page_number)
    
    return render(request, 'gestion/lista_equipos.html', {
        'lista_equipos': equipos_paginados, # Ahora es un objeto paginado
        'counts': counts,
        'tipo_actual': tipo # Coincide con el HTML corregido
    })

def historial_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo.objects.prefetch_related('ficha'), id=equipo_id)
    return render(request, 'gestion/historial_equipo.html', {
        'equipo': equipo,
        'ordenes': sel.get_historial_equipo(equipo_id)
    })

def calendario_taller(request):
    hoy = datetime.now()
    try:
        mes = int(request.GET.get('mes', hoy.month))
        anio = int(request.GET.get('anio', hoy.year))
    except ValueError:
        mes, anio = hoy.month, hoy.year
        
    contexto = ServicioCalendario.generar_contexto(anio, mes)
    
    # Le pasamos un formulario vacío para renderizar en el modal
    contexto['form_evento'] = EventoCalendarioForm() 
    
    return render(request, 'gestion/calendario.html', contexto)

def crear_evento_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = EventoCalendarioForm(data)
            
            if form.is_valid():
                form.save()
                return api_success()
                
            return api_error(errors=form.errors)
            
        except Exception as e:
            return api_error(message=str(e), status=500)
            
    return api_error(message='Método no permitido', status=405)

def configuracion_sistema(request):
    productos = Producto.objects.all()
    return render(request, 'gestion/configuracion.html', {'productos': productos})

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    if request.method == 'POST':
        if svc.actualizar_cliente(cliente, request.POST):
            return redirect('lista_clientes')
        # Si falla, el form con errores se vuelve a renderizar abajo
    
    form = ClienteForm(instance=cliente)
    return render(request, 'gestion/editar_cliente.html', {
        'form': form,
        'cliente': cliente
    })