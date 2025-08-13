@echo off
REM Quick start for Jupyter notebook with venv

echo Starting Jupyter Notebook with OptionMonger venv...
cd ..
call venv\Scripts\activate.bat
jupyter notebook notebooks\live_options_trading_optimized.ipynb