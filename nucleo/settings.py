from pathlib import Path
import os
from dotenv import load_dotenv
# --- CARGAR VARIABLES DE ENTORNO (.env) ---
load_dotenv()

# --- PARCHE PARA SQL SERVER 2022 (Librería mssql-django) ---
# Obligatorio: Engaña a la librería para que crea que es la versión 2019
import mssql.base
try:
    mssql.base.DatabaseWrapper.sql_server_version = property(lambda self: 2019)
except Exception:
    pass
# -----------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
# --- SEGURIDAD BLINDADA ---
# Toma la clave secreta del .env
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-clave-por-defecto')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# Convierte el string del .env (ej: "localhost,192.168.101.84") en una lista de Python
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = allowed_hosts_env.split(',') if allowed_hosts_env else []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion',
    'iot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nucleo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nucleo.wsgi.application'

# --- BASE DE DATOS (Configuración para mssql-django) ---
DATABASES = {
    'default': {
        'ENGINE': 'mssql', 
        'NAME': os.getenv('DB_NAME', 'GestionTallerDB'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'USER': os.getenv('DB_USER', ''),       # Queda vacío si usas Windows Authentication
        'PASSWORD': os.getenv('DB_PASSWORD', ''), # Queda vacío si usas Windows Authentication
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'nucleo' / 'static',]
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

print(">>> DEBUG: Configuración mssql-django cargada <<<")

# --- CONFIGURACIÓN DE ARCHIVOS MULTIMEDIA (FOTOS) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# ----------------------------------------------------