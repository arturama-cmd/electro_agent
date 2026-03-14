@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ============================================
echo   ElectroAgent - Setup and Run Script
echo   Windows 11 Desktop Initialization
echo ============================================
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [1/7] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no encontrado en PATH
    echo         Instala Python 3.8+ desde https://python.org
    echo         Asegurate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% encontrado

echo.
echo [2/7] Verificando entorno virtual...
if not exist "venv\Scripts\activate.bat" (
    echo     Creando entorno virtual...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
) else (
    echo [OK] Entorno virtual existente
)

echo.
echo [3/7] Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado

echo.
echo [4/7] Verificando/instalando dependencias Python...
pip show streamlit >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo     Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Fallo la instalacion de dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
) else (
    echo [OK] Dependencias ya instaladas
    echo     Verificando actualizaciones...
    pip install -r requirements.txt --quiet --upgrade
)

echo.
echo [5/7] Verificando Tesseract OCR...
set "TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe"
if exist "%TESSERACT_PATH%" (
    echo [OK] Tesseract OCR encontrado
) else (
    echo [WARN] Tesseract OCR no encontrado en:
    echo        %TESSERACT_PATH%
    echo.
    echo        PDFs escaneados NO podran ser procesados con OCR.
    echo        Para instalar Tesseract:
    echo        1. Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki
    echo        2. Instala en: C:\Program Files\Tesseract-OCR
    echo        3. Durante instalacion, selecciona idioma "Spanish"
    echo.
)

echo.
echo [6/7] Verificando Poppler (PDF tools)...
set "POPPLER_PATH=%PROJECT_DIR%poppler-24.08.0\Library\bin"
if exist "%POPPLER_PATH%\pdftoppm.exe" (
    echo [OK] Poppler encontrado en proyecto
) else (
    echo [WARN] Poppler no encontrado en:
    echo        %POPPLER_PATH%
    echo.
    echo        Conversion PDF a imagen para OCR no disponible.
    echo        Descarga Poppler desde: https://github.com/osber/poppler/releases
    echo.
)

echo.
echo [7/7] Verificando configuracion API...
if exist ".env" (
    findstr /C:"ANTHROPIC_API_KEY" .env >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Archivo .env con ANTHROPIC_API_KEY encontrado
    ) else (
        echo [ERROR] Archivo .env existe pero no contiene ANTHROPIC_API_KEY
        echo         Agrega: ANTHROPIC_API_KEY=tu-api-key
        pause
        exit /b 1
    )
) else (
    if exist ".env.local.example" (
        echo [WARN] Archivo .env no encontrado
        echo        Copiando desde .env.local.example...
        copy ".env.local.example" ".env" >nul
        echo [ACTION] Edita el archivo .env y agrega tu ANTHROPIC_API_KEY
        notepad ".env"
        pause
    ) else (
        echo [ERROR] Archivo .env no encontrado
        echo         Crea un archivo .env con: ANTHROPIC_API_KEY=tu-api-key
        echo ANTHROPIC_API_KEY=tu-api-key-aqui > .env
        echo [ACTION] Edita el archivo .env con tu API key real
        notepad ".env"
        pause
    )
)

echo.
echo ============================================
echo   Verificacion completada
echo ============================================
echo.
echo Iniciando ElectroAgent...
echo (La aplicacion se abrira en tu navegador)
echo.
echo Presiona Ctrl+C en esta ventana para detener el servidor
echo.

streamlit run app.py

pause
