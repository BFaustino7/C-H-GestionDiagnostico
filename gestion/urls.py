from django.urls import path
from . import views

urlpatterns = [
    # Ruta de la pantalla principal (Tablero)
    path('', views.tablero_principal, name='tablero'),

    # --- NUEVA RUTA DE DETALLE ---
    path('orden/<int:orden_id>/', views.detalle_orden, name='detalle_orden'),
    # -----------------------------

    # Ruta para imprimir el remito
    path('remito/<int:orden_id>/', views.imprimir_remito, name='imprimir_remito'),
]