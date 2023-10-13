setlocal enabledelayedexpansion
set "PYTHON=python"
echo "Launching..."
cd %CD%
set "USER=%USERNAME%"
echo Current User = %USER%
call .\venv\scripts\activate.bat
echo "venv activated"
python --version
python -s similar-image-search.py
pause