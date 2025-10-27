@echo off
echo ============================================================
echo WhatsApp Bot - Iniciando Servidor FastAPI
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando dependencias...
python -c "import fastapi; import uvicorn; print('FastAPI e Uvicorn instalados')"
if errorlevel 1 (
    echo ERRO: FastAPI ou Uvicorn nao instalados!
    echo Execute: pip install fastapi uvicorn
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando servidor...
echo.
echo ============================================================
echo Servidor rodando em: http://localhost:8000
echo Acesse: http://localhost:8000/health para verificar status
echo Pressione CTRL+C para parar
echo ============================================================
echo.

python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

pause
