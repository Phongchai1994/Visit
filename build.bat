
@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Visit - Build Installer

echo ========================================
echo       VISIT INSTALLER BUILDER
echo ========================================
echo.

REM ========================================
REM STEP 1: Check required files
REM ========================================

echo [1/5] Checking requirements...

if not exist "main.py" (
    echo [ERROR] main.py not found.
    goto :failed
)

if not exist "Visit.spec" (
    echo [ERROR] Visit.spec not found.
    goto :failed
)

if not exist "installer.iss" (
    echo [ERROR] installer.iss not found.
    goto :failed
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python environment not found.
    goto :failed
)

".venv\Scripts\python.exe" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed.
    goto :failed
)

REM ========================================
REM STEP 2: Find Inno Setup
REM ========================================

echo [2/5] Finding Inno Setup...

set "ISCC="

if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"

if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"

if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    for %%I in (ISCC.exe) do (
        if not "%%~$PATH:I"=="" set "ISCC=%%~$PATH:I"
    )
)

if not defined ISCC (
    echo [ERROR] Inno Setup Compiler not found.
    goto :failed
)

REM ========================================
REM STEP 3: Build Visit.exe
REM ========================================

echo.
echo [3/5] Building Visit.exe...

REM Remove previous generated files
if exist "dist\Visit" rmdir /s /q "dist\Visit"

if exist "dist\Visit" (
    echo [ERROR] Cannot clean previous dist.
    goto :failed
)

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean "Visit.spec"

if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    goto :failed
)

if not exist "dist\Visit\Visit.exe" (
    echo [ERROR] Visit.exe was not created.
    goto :failed
)

REM ========================================
REM STEP 4: Exclude sensitive files
REM ========================================

echo.
echo [4/5] Checking packaged files...

REM Remove .env files from dist only
for /r "dist\Visit" %%F in (.env) do (
    if exist "%%~fF" (
        echo [INFO] Removing: %%~fF
        del /f /q "%%~fF"
    )
)

REM Block secrets and database files
for /r "dist\Visit" %%F in (*.db *.db.enc *.sqlite *.sqlite3 *.key .env) do (
    if exist "%%~fF" (
        echo [ERROR] Sensitive file found: %%~fF
        goto :failed
    )
)

echo [OK] No sensitive files detected.

REM ========================================
REM STEP 5: Create installer
REM ========================================

echo.
echo [5/5] Compiling Inno Setup...

"%ISCC%" "installer.iss"

if errorlevel 1 (
    echo [ERROR] Inno Setup compilation failed.
    goto :failed
)

echo.
echo ========================================
echo [SUCCESS] BUILD COMPLETED
echo ========================================
echo.

echo Installer folder:
echo %CD%\installer_output

echo.
start "" explorer.exe "%CD%\installer_output"

pause
exit /b 0

:failed
echo.
echo ========================================
echo [FAILED] BUILD STOPPED
echo ========================================
echo Please review the errors above.
echo.
pause
exit /b 1
