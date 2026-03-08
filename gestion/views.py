from django.shortcuts import render, get_object_or_404
from .models import OrdenReparacion
import random
from datetime import datetime, timedelta

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
            
            # Valores actuales (último de la lista)
            'presion_baja_val': int(historial_presion_baja[-1]),
            'presion_alta_val': int(historial_alta[-1]),
            'temp_val': historial_temp[-1],
            'sh_val': historial_superheat[-1], # <--- NUEVO VALOR
            'watts_val': historial_watts[-1],
            
            # Listas para gráficos
            'data_baja': historial_presion_baja,
            'data_alta': historial_alta,
            'data_temp': historial_temp,
            'data_watts': historial_watts,
            'data_sh': historial_superheat,
            'labels': labels,
        })

    return render(request, 'gestion/tablero.html', {
        'taller': ordenes_taller,
        'entregas': ordenes_para_entregar,
        'historial': ordenes_entregadas,
        'banco_pruebas': banco_pruebas,
    })

# --- VISTAS SECUNDARIAS ---

def imprimir_remito(request, orden_id):
    orden = get_object_or_404(OrdenReparacion, pk=orden_id)
    return render(request, 'gestion/remito_imprimible.html', {'orden': orden})

def detalle_orden(request, orden_id):
    try:
        orden = OrdenReparacion.objects.get(pk=orden_id)
    except OrdenReparacion.DoesNotExist:
        return render(request, 'gestion/orden_no_encontrada.html', {
            'id_buscado': orden_id
        })
    
    return render(request, 'gestion/detalle_orden.html', {
        'orden': orden,
    })