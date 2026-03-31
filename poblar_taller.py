import os
import django
import random
from datetime import datetime, timedelta

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo.settings') # Cambiá 'SR_Gestion' por el nombre de tu proyecto si es distinto
django.setup()

from gestion.models import Cliente, Equipo, OrdenReparacion

def poblar():
    # 1. LIMPIEZA (Opcional: borra todo para empezar de cero)
    print("Limpiando base de datos de prueba...")
    OrdenReparacion.objects.all().delete()
    Equipo.objects.all().delete()
    Cliente.objects.all().delete()

    # 2. CREACIÓN CONTROLADA
    nombres = ['Juan Perez', 'Maria Garcia', 'Talleres Rosario']
    
    for n in nombres:
        # get_or_create evita que se duplique el cliente si ya existe
        c, _ = Cliente.objects.get_or_create(nombre=n, telefono='3415551234')
        
        e = Equipo.objects.create(
            cliente=c, 
            marca=random.choice(['BGH', 'Samsung', 'Surrey']),
            modelo='Inverter 4500',
            tipo='AIRE'
        )

        # 3. CREAR SOLO 1 ORDEN POR EQUIPO PARA PROBAR
        estados = ['PENDIENTE', 'DIAGNOSTICO', 'REPARACION']
        OrdenReparacion.objects.create(
            equipo=e,
            estado=random.choice(estados),
            falla_declarada="No enfría correctamente",
            costo_mano_obra=random.randint(5000, 15000)
        )

    print(">>> Base de datos poblada con 3 registros limpios.")
    if __name__ == "__main__":
        poblar()