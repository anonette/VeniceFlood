@echo off
echo ===================================
echo Venice Flat Ontology Setup
echo ===================================

echo.
echo Step 1: Creating Python virtual environment...
python -m venv venice_env

echo.
echo Step 2: Activating virtual environment...
call venice_env\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing requirements...
pip install -r requirements.txt

echo.
echo ===================================
echo Setup Complete!
echo ===================================
echo.
echo To activate environment in future sessions:
echo   venice_env\Scripts\activate.bat
echo.
echo To start Venice simulation:
echo   python scripts\create_venice_agents.py
echo.
echo Press any key to continue...
pause
