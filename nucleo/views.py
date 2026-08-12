import os
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404


@login_required
def servir_media(request, ruta):
    """Sirve archivos de media de forma segura solo para usuarios autenticados."""
    ruta_segura = (Path(settings.MEDIA_ROOT) / ruta).resolve()
    if not str(ruta_segura).startswith(str(Path(settings.MEDIA_ROOT).resolve())):
        raise Http404
    if not ruta_segura.is_file():
        raise Http404
    return FileResponse(ruta_segura.open('rb'))