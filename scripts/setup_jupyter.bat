@echo off
REM Windows batch file to setup Jupyter with venv

echo ============================================================
echo Setting up Jupyter with venv
echo ============================================================
echo.

REM Activate venv
echo 1. Activating venv...
call venv\Scripts\activate.bat

REM Install Jupyter and dependencies
echo 2. Installing Jupyter and dependencies...
pip install jupyter ipykernel matplotlib

REM Create a kernel for this venv
echo 3. Creating Jupyter kernel for OptionMonger...
python -m ipykernel install --user --name=optionmonger --display-name="OptionMonger (venv)"

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To use the notebook:
echo 1. Run: jupyter notebook live_options_trading.ipynb
echo 2. In Jupyter, go to Kernel - Change Kernel - OptionMonger (venv)
echo.
echo Or start directly with the correct kernel:
echo jupyter notebook --kernel=optionmonger live_options_trading.ipynb
echo ============================================================
pause