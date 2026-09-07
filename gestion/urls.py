from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # 1. Ruta de la pantalla principal (Tablero)
    path('', views.tablero_principal, name='tablero'),
    # --- NUEVA RUTA DE DETALLE ---
    path('orden/<int:orden_id>/', views.detalle_orden, name='detalle_orden'),
    # Ruta para imprimir el remito
    path('remito/<int:orden_id>/', views.imprimir_remito, name='imprimir_remito'),
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    # --- RUTAS DE AUTENTICACIÓN ---
    path('login/', auth_views.LoginView.as_view(template_name='gestion/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registro/', views.registro_usuario, name='registro'),
    # --- MISMA RUTA (única) ---
    path('calendario/', views.calendario_taller, name='calendario'),
    path('configuracion/', views.configuracion_sistema, name='configuracion'),
    path('ingresar/', views.ingreso_equipo, name='ingreso_equipo'),
    path('equipo/historial/<int:equipo_id>/', views.historial_equipo, name='historial_equipo'),
    path('cliente/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('api/eventos/crear/', views.crear_evento_api, name='crear_evento_api')
]