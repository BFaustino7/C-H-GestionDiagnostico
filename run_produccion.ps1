# ============================================
# ARRANQUE DE PRODUCCION — C&H GestionDiagnostico
# Uso: .\run_produccion.ps1
# Levanta Django con waitress + modo seguro (DEBUG=False, PRODUCTION=True)
# para exponerlo detras de Cloudflare Tunnel.
# El .env de desarrollo (DEBUG=True) queda intacto.
# ============================================

$ErrorActionPreference = "Stop"

# Modo seguro explicito (sobreescribe .env para este proceso unicamente)
$env:DEBUG = "False"
$env:PRODUCTION = "True"

# 1) Recolectar estaticos (CSS/JS) para whitenoise
Write-Host "[1/3] Recolectando estaticos..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) { throw "collectstatic fallo" }

# 2) Verificar configuracion
Write-Host "[2/3] Verificando configuracion..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" manage.py check
if ($LASTEXITCODE -ne 0) { throw "check fallo" }

# 3) Servidor real (waitress) en todas las interfaces
Write-Host "[3/3] Levantando waitress en 0.0.0.0:8000 (Ctrl+C para detener)" -ForegroundColor Green
& ".\.venv\Scripts\python.exe" -m waitress --listen=0.0.0.0:8000 nucleo.wsgi:application