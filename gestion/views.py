# --- LIBRERÍAS ESTÁNDAR ---
from datetime import datetime

# --- CORE DE DJANGO ---
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Q
from .services import procesar_insumos_orden

# --- MODELOS Y FORMULARIOS LOCALES ---
from .models import OrdenReparacion, FichaTecnica, Cliente, Equipo, Producto, DetalleInsumo
from .forms import ClienteForm, EquipoForm, OrdenIngresoForm, OrdenTecnicaForm, EspecificacionesForm

# --- SERVICIOS EXTERNOS ---
from iot.iot_simulador import generar_datos_banco_pruebas


def ingreso_equipo(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        equipo_form = EquipoForm(request.POST)
        orden_form = OrdenIngresoForm(request.POST)

        if cliente_form.is_valid() and equipo_form.is_valid() and orden_form.is_valid():
            try:
                with transaction.atomic():
                    cliente = cliente_form.save()

                    equipo = equipo_form.save(commit=False)
                    equipo.cliente = cliente
                    equipo.save()

                    FichaTecnica.objects.create(
                        equipo=equipo,
                        gas_tipo='',
                        gas_cantidad=0,
                        datos_electricos=''
                    )

                    orden = orden_form.save(commit=False)
                    orden.equipo = equipo
                    orden.save()

                return redirect('tablero') 
            
            except Exception as e:
                pass
    else:
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
    ordenes_taller = OrdenReparacion.objects.filter(
        estado__in=['PENDIENTE', 'DIAGNOSTICO', 'ESPERA', 'REPARACION']
    ).order_by('-fecha_ingreso')

    ordenes_para_entregar = OrdenReparacion.objects.filter(estado='TERMINADO').order_by('-fecha_ingreso')
    ordenes_entregadas = OrdenReparacion.objects.filter(estado='ENTREGADO').order_by('-fecha_ingreso')[:5]

    equipos_en_banco = ordenes_taller.filter(estado='REPARACION')
    if not equipos_en_banco:
        equipos_en_banco = ordenes_taller.filter(estado='DIAGNOSTICO')

    # Llamada a la función extraída en iot_simulador.py
    banco_pruebas = generar_datos_banco_pruebas(equipos_en_banco)

    return render(request, 'gestion/tablero.html', {
        'ordenes_en_proceso': ordenes_taller, 
        'ordenes_para_entregar': ordenes_para_entregar,
        'ordenes_entregadas': ordenes_entregadas,
        'banco_pruebas': banco_pruebas,
    })


def imprimir_remito(request, orden_id):
    orden = get_object_or_404(OrdenReparacion, pk=orden_id)
    return render(request, 'gestion/remito_imprimible.html', {'orden': orden})


def detalle_orden(request, orden_id):
    orden = get_object_or_404(OrdenReparacion, pk=orden_id)
    ficha, _ = FichaTecnica.objects.get_or_create(equipo=orden.equipo)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        # Pasamos el diccionario JSON a los formularios
        form_orden = OrdenTecnicaForm(data, instance=orden)
        form_ficha = EspecificacionesForm(data, instance=ficha)

        if form_orden.is_valid() and form_ficha.is_valid():
            form_orden.save()
            form_ficha.save()

            # Delegar el bucle a la capa de servicios
            procesar_insumos_orden(orden, data.get('insumos', []))
                
            return JsonResponse({'status': 'success'})
        else:
            errors = {**form_orden.errors, **form_ficha.errors}
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)

    else:
        form_orden = OrdenTecnicaForm(instance=orden)
        form_ficha = EspecificacionesForm(instance=ficha)

    #La vista ya no hace cálculos matemáticos ni consultas extra
    context = {
        'orden': orden,
        'form_orden': form_orden,
        'form_ficha': form_ficha,
        'total_general': orden.total_calculado # Delegado al modelo
    }
    
    return render(request, 'gestion/detalle_orden.html', context)

def lista_clientes(request):
    busqueda = request.GET.get('buscar')
    if busqueda:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=busqueda) | Q(telefono__icontains=busqueda)
        )
    else:
        clientes = Cliente.objects.all().order_by('nombre')
    
    return render(request, 'gestion/lista_clientes.html', {'lista_clientes': clientes})


def lista_equipos(request):
    tipo_filtro = request.GET.get('tipo')
    # select_related('cliente') y prefetch_related('ficha') 
    # para traer todo de un solo viaje a la DB (Optimización Pro)
    equipos = Equipo.objects.select_related('cliente').prefetch_related('ficha').all()

    # 1. Contadores para los botones de arriba, empaquetados (Calculados sobre el total, antes del filtro)
    counts = {
        'count_total': equipos.count(),
        'count_split': equipos.filter(tipo='SPLIT').count(),
        'count_heladera': equipos.filter(Q(tipo='HELADERA') | Q(tipo='COMERCIAL')).count(),
        'count_lavarropas': equipos.filter(tipo='LAVARROPAS').count(),
    }


    # 2. Aplicar el filtro al QuerySet que se va a mostrar
    equipos_a_renderizar = equipos
    if tipo_filtro:
        tipo_upper = tipo_filtro.upper()
        if tipo_upper == 'HELADERA':
            equipos_a_renderizar = equipos.filter(Q(tipo='HELADERA') | Q(tipo='COMERCIAL'))
        else:
            equipos_a_renderizar = equipos.filter(tipo=tipo_upper)

    return render(request, 'gestion/lista_equipos.html', {
        'lista_equipos': equipos_a_renderizar,
        'counts': counts,
        'tipo_actual': tipo_filtro
    })

def calendario_taller(request):
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


def historial_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    ordenes = OrdenReparacion.objects.filter(equipo=equipo).order_by('-fecha_ingreso')
    
    context = {
        'equipo': equipo,
        'ordenes': ordenes,
    }
    
    return render(request, 'gestion/historial_equipo.html', context)