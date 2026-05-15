@echo off
REM Builds Everdell_2.0.1.1056_RU.exe from install_russian.py.
REM Bundles game.cfg and localization into the exe and embeds an
REM admin manifest (--uac-admin) so it can write into Program Files.

cd /d "%~dp0"

echo Installing PyInstaller (if needed)...
python -m pip install --upgrade pyinstaller || goto :fail

echo.
echo Building exe...
python -m PyInstaller --onefile --uac-admin --clean ^
  --name "Everdell_2.0.1.1056_RU" ^
  --add-data "2.0.1.1056\game.cfg;." ^
  --add-data "2.0.1.1056\localization;." ^
  install_russian.py || goto :fail

echo.
echo DONE. The exe is here:
echo   %~dp0dist\Everdell_2.0.1.1056_RU.exe
echo.
pause
exit /b 0

:fail
echo.
echo BUILD FAILED.
pause
exit /b 1
