@echo off
setlocal enabledelayedexpansion
set "PYTHON=python"
echo "Launching..."
cd %CD%
set "USER=%USERNAME%"
echo Current User = %USER%
call .\venv\scripts\activate.bat
echo "venv activated"
python --version
echo.
python -s similar-image-search.py --threshold 0.30 --num_similar 10 %CD%\reference.jpg %CD%\test
pause