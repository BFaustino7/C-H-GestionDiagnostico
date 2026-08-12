# =====================================================================
# CONSTANTES CANÓNICAS DEL SISTEMA
# =====================================================================
# Un solo lugar para los valores que se repiten en modelos, vistas,
# selectors, admin y templates. Si hay que cambiar un estado, se cambia
# SOLO acá y todo el sistema queda consistente.

# --- Estados de una Orden de Reparación ---
ESTADOS_ORDEN = [
    ('PENDIENTE', 'Pendiente'),
    ('DIAGNOSTICO', 'Diagnóstico'),
    ('REPARACION', 'Reparación'),
    ('COMPLETADO', 'Completado'),
    ('ENTREGADO', 'Entregado'),
]

# Diccionario útil para admin/templates: estado -> etiqueta
ESTADOS_ORDEN_DICT = dict(ESTADOS_ORDEN)

# Subconjuntos usados en los filtros del tablero
ESTADOS_EN_PROCESO = ['PENDIENTE', 'DIAGNOSTICO', 'REPARACION']
ESTADOS_EN_BANCO_PRUEBAS = ['DIAGNOSTICO', 'REPARACION']
ESTADOS_PARA_ENTREGAR = ['COMPLETADO']
ESTADOS_ENTREGADOS = ['ENTREGADO']

# --- Tipos de Equipo ---
TIPOS_EQUIPO = [
    ('SPLIT', 'Aire Acondicionado Split'),
    ('VENTANA', 'Aire Acondicionado Ventana'),
    ('HELADERA', 'Heladera Familiar'),
    ('COMERCIAL', 'Heladera Comercial/Exhibidora'),
    ('CAMARA', 'Cámara Frigorífica'),
    ('LAVARROPAS', 'Lavarropas'),
]

# --- Estados de Pago ---
ESTADOS_PAGO = [
    ('DEBE', 'Impago'),
    ('SENA', 'Seña / Anticipo'),
    ('PAGADO', 'Pagado Totalmente'),
]

# --- Tipos de Evento de Calendario ---
TIPOS_EVENTO = [
    ('TURNO', 'Turno / Visita'),
    ('ENTREGA', 'Entrega de Equipo'),
    ('ALERTA', 'Alerta / Recordatorio'),
]
