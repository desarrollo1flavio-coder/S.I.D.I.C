@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM  S.I.D.I.C - Sistema de Información Delictual e Inteligencia Criminal
REM  Script de instalación para Windows
REM ═══════════════════════════════════════════════════════════════════════

echo.
echo ════════════════════════════════════════════════════════════════════
echo   S.I.D.I.C - Instalador
echo   Sistema de Información Delictual e Inteligencia Criminal
echo ════════════════════════════════════════════════════════════════════
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    echo.
    echo Por favor instale Python 3.11 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrese de marcar "Add Python to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Crear entorno virtual
echo [*] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado
echo.

REM Activar entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

REM Actualizar pip
echo [*] Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo [*] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar algunas dependencias
    echo Intente instalarlas manualmente con: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.
echo [OK] Dependencias instaladas
echo.

REM Crear acceso directo
echo [*] Creando script de ejecución...
echo @echo off > run_sidic.bat
echo call venv\Scripts\activate.bat >> run_sidic.bat
echo cd src >> run_sidic.bat
echo python main.py >> run_sidic.bat
echo [OK] Script de ejecución creado: run_sidic.bat
echo.

echo ════════════════════════════════════════════════════════════════════
echo   ¡INSTALACIÓN COMPLETADA!
echo ════════════════════════════════════════════════════════════════════
echo.
echo   Para ejecutar S.I.D.I.C, use uno de estos métodos:
echo.
echo   1. Doble clic en: run_sidic.bat
echo.
echo   2. Desde la línea de comandos:
echo      cd %CD%
echo      venv\Scripts\activate
echo      cd src
echo      python main.py
echo.
echo ════════════════════════════════════════════════════════════════════
echo.
pause
