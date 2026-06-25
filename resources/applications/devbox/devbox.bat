@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "home_path=%~dp0"

for %%I in ("%home_path%.") do set "current_path=%%~fI"

:find_project_root
if exist "%current_path%\.root" (
    set "ROOT_FILE=%current_path%\.root"

    powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; try { $content = [System.IO.File]::ReadAllText($env:ROOT_FILE, [System.Text.Encoding]::UTF8).Trim(); if ($content -ceq 'project-root') { exit 0 }; exit 1 } catch { exit 1 }" >nul 2>&1

    if not errorlevel 1 (
        set "projekt_root_path=%current_path%"
        goto :project_root_found
    )
)

for %%I in ("%current_path%\..") do set "parent_path=%%~fI"

if /i "%parent_path%"=="%current_path%" (
    echo No project root found.
    exit /b 0
)

set "current_path=%parent_path%"
goto :find_project_root

:project_root_found
set "devbox_launcher=%projekt_root_path%\resources\applications\devbox\functions\devbox_launcher.py"

if not exist "%devbox_launcher%" (
    echo DevBox launcher not found:
    echo %devbox_launcher%
    exit /b 0
)

set "python_exe="

for /f "delims=" %%A in ('where.exe python.exe 2^>nul') do (
    if not defined python_exe set "python_exe=%%A"
)

if not defined python_exe (
    echo python.exe was not found in PATH.
    exit /b 0
)

set "DEVBOX_PYTHON_EXE=%python_exe%"
set "DEVBOX_LAUNCHER=%devbox_launcher%"
set "DEVBOX_WORKING_DIRECTORY=%projekt_root_path%"

powershell.exe -NoProfile -WindowStyle Hidden -Command "$argument = '\"' + $env:DEVBOX_LAUNCHER + '\"'; Start-Process -FilePath $env:DEVBOX_PYTHON_EXE -ArgumentList $argument -WorkingDirectory $env:DEVBOX_WORKING_DIRECTORY -WindowStyle Hidden"

exit /b 0