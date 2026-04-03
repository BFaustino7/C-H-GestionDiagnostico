from django.urls import path
from . import views

urlpatterns = [
    # Ruta de la pantalla principal (Tablero)
    path('', views.tablero_principal, name='tablero'),
    # --- NUEVA RUTA DE DETALLE ---
    path('orden/<int:orden_id>/', views.detalle_orden, name='detalle_orden'),
    # Ruta para imprimir el remito
    path('remito/<int:orden_id>/', views.imprimir_remito, name='imprimir_remito'),
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('calendario/', views.calendario_taller, name='calendario'),
    path('configuracion/', views.configuracion_sistema, name='configuracion'),
    path('ingresar/', views.ingreso_equipo, name= 'ingreso_equipo'),
    path('equipo/historial/<int:equipo_id>/', views.historial_equipo, name='historial_equipo'),
    path('cliente/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('calendario/', views.calendario_taller, name='calendario'),
    path('api/eventos/crear/', views.crear_evento_api, name='crear_evento_api')
]