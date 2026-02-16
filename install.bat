@echo off
REM Script de instalação para Windows

echo ======================================
echo Instalando Sistema de Automacao Sirius
echo ======================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale o Python 3.8 ou superior em https://python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Instala dependencias
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas
echo.

REM Cria arquivo de credenciais se nao existir
if not exist config\credentials.env (
    echo Criando arquivo de credenciais...
    copy config\credentials.env.example config\credentials.env
    echo.
    echo ======================================
    echo ATENCAO: Configure suas credenciais!
    echo ======================================
    echo Edite o arquivo: config\credentials.env
    echo.
    notepad config\credentials.env
)

echo.
echo ======================================
echo Instalacao concluida!
echo ======================================
echo.
echo Para executar:
echo   python main.py
echo.
echo Para ajuda:
echo   python main.py --help
echo.

pause
