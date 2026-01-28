@echo off
setlocal

cd /d %~dp0

echo =====================================
echo Week3 RAG Agent - Local Runner (Py 3.12)
echo =====================================
echo.

echo [INFO] Available Python versions:
py -0
echo.

if not exist .venv (
    echo [STEP] Creating venv with Python 3.12...
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create venv with Python 3.12.
        goto END
    )
)

echo [STEP] Activating venv...
call .venv\Scripts\activate

echo [INFO] Python in venv:
python --version
echo.

echo [STEP] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    goto END
)

echo.
echo [STEP] Starting FastAPI server...
echo.

python -m uvicorn app.main:app --reload

:END
echo.
echo =====================================
echo Islem tamamlandi veya hata alindi.
echo Kapatmak icin bir tusa basin...
echo =====================================
pause >nul

endlocal
