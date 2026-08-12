"""
Configuración de testing con SQLite para evitar problemas con MSSQL en el entorno de desarrollo.
"""
from .settings import *  # noqa

# Base de datos de prueba en SQLite (archivo en el directorio del proyecto)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test_pruebas.sqlite3',
    }
}

# Media files también en SQLite para pruebas
MEDIA_ROOT = BASE_DIR / 'media_test'

# Sin depuración para pruebas más realistas
DEBUG = False

# Servidores permitidos para tests
ALLOWED_HOSTS = ['localhost', '127.0.0.1']