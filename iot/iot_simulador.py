import random
from datetime import datetime, timedelta

def generar_datos_banco_pruebas(equipos_en_banco):
    banco_pruebas = []
    
    for orden in equipos_en_banco:
        historial_presion_baja = []
        historial_temp = []
        historial_superheat = []
        historial_amp = []
        historial_watts = []
        historial_alta = []

        for _ in range(10):
            p_baja = round(random.uniform(115, 125), 1)
            historial_presion_baja.append(p_baja)

            t_sat = (p_baja - 100) * 0.2 + 2 
            
            sh_simulado = round(random.uniform(4.0, 9.0), 1)
            historial_superheat.append(sh_simulado)

            t_retorno = round(t_sat + sh_simulado, 1)
            historial_temp.append(t_retorno)

            amp = round(random.uniform(3.5, 4.2), 1)
            historial_amp.append(amp)
            
            voltaje = random.randint(218, 223)
            historial_watts.append(int(voltaje * amp))
            
            historial_alta.append(int(p_baja * 3.2))

        ahora = datetime.now()
        labels = [(ahora - timedelta(minutes=i)).strftime("%H:%M") for i in range(10, 0, -1)]

        banco_pruebas.append({
            'id': orden.id,
            'equipo_marca': f"{orden.equipo.marca} {orden.equipo.modelo}",
            'baja_presion': int(historial_presion_baja[-1]),
            'alta_presion': int(historial_alta[-1]),
            'temperatura': historial_temp[-1],
            'superheat': historial_superheat[-1],
            'potencia': historial_watts[-1],
            'baja_presion_data': historial_presion_baja,
            'alta_presion_data': historial_alta,
            'temperatura_data': historial_temp,
            'superheat_data': historial_superheat,
            'potencia_data': historial_watts,
            'labels': labels,
        })
        
    return banco_pruebas