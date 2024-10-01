@echo off
setlocal enabledelayedexpansion

:: Check if arguments are provided
if "%~1"=="" (
    echo Not enough arguments. Path to an environment variable file must be provided as an argument.
    exit /b 2
) else if not "%~2"=="" (
    echo Too many arguments. Only the first argument is inferred as the path to an environment variable file; all others are ignored.
)

set "ENV_FILE=%~1"

echo Starting application with values loaded from %ENV_FILE%

:: Load environment variables from the file
for /f "tokens=1,* delims==" %%a in (%ENV_FILE%) do (
    set "%%a=%%b"
)

:: Run the Python application
python app.py