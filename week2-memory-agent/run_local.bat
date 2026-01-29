@echo off
setlocal

REM Her zaman bu .bat dosyasinin oldugu dizinden calis
cd /d %~dp0

echo =====================================
echo Week2 Memory Agent - Local Runner
echo =====================================
echo.

echo [INFO] Python path:
where python
python --version
echo.

REM VENV olustur
if not exist .venv (
    echo [STEP] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Virtual environment could not be created.
        goto END
    )
)

echo [STEP] Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo [ERROR] Virtual environment activation failed.
    goto END
)

echo [STEP] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Pip upgrade failed.
    goto END
)

echo [STEP] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    goto END
)

echo.
echo [STEP] Starting FastAPI server...
echo (Press CTRL+C to stop the server)
echo.

python -m uvicorn app.main:app --reload
echo.

:END
echo =====================================
echo Islem tamamlandi veya hata alindi.
echo Kapatmak icin bir tusa basin...
echo =====================================
pause >nul

endlocal
