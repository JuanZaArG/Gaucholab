@echo off
setlocal

if not exist .venv (
    echo [INFO] Creating virtual environment...
    python -m venv .venv || goto :end
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

pyinstaller ^
    --name MultiAndroidLab ^
    --onefile ^
    --add-data "multi_android_lab/assets;multi_android_lab/assets" ^
    --noconsole ^
    -m multi_android_lab.main

echo.
echo Hecho. El binario se encuentra en dist\MultiAndroidLab.exe

:end
endlocal
