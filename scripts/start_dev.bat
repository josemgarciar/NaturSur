@echo off
REM Development startup helper for Windows
REM Runs migrations, seeds offerings, then starts the dev server

setlocal enabledelayedexpansion

REM Get the root directory (parent of scripts folder)
for %%I in ("%~dp0..") do set "ROOT_DIR=%%~fI"

cd /d "%ROOT_DIR%"

REM If there is a .venv in the project, activate it
if exist "%ROOT_DIR%\.venv\Scripts\activate.bat" (
	call "%ROOT_DIR%\.venv\Scripts\activate.bat"
	echo [*] Activated virtualenv at %ROOT_DIR%\.venv
)

echo [*] Applying migrations...
python manage.py migrate

echo [*] Seeding offerings...
REM Run the seeder under manage.py shell so project root is on sys.path
python manage.py shell < scripts\seed_offerings.py

REM Set default host:port if not provided
if "%~1"=="" (
	set "HOSTPORT=127.0.0.1:8000"
) else (
	set "HOSTPORT=%~1"
)

echo [*] Starting development server at http://%HOSTPORT%/
python manage.py runserver %HOSTPORT%
