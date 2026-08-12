from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import servir_media

urlpatterns = [
    # 1. Ruta del Panel de Administración
    path('admin/', admin.site.urls),

    # 2. Ruta Principal: Le dice a Django "Busca las rutas en la carpeta gestion"
    path('', include('gestion.urls')),

    # 3. Rutas de medios (solo cuando DEBUG=False, para producción en LAN)
    path('media/<path:ruta>', servir_media, name='servir_media'),
]

# Configuración para ver las fotos subidas
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)