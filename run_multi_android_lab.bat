@echo off
setlocal

REM --- Optional: set the path to your ADB and scrcpy binaries here ---
REM set MULTI_ANDROID_LAB_ADB=C:\path\to\adb.exe
REM set MULTI_ANDROID_LAB_SCRCPY=C:\path\to\scrcpy.exe

pushd %~dp0

if not exist .venv (
    echo [INFO] Creating virtual environment...
    python -m venv .venv || goto :end
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip >NUL
python -m pip install -r requirements.txt >NUL 2>&1

python -m multi_android_lab.main %*

:end
popd
endlocal
