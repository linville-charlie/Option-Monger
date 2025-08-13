#!/bin/bash
# Setup Jupyter notebook with venv

echo "============================================================"
echo "Setting up Jupyter with venv"
echo "============================================================"
echo

# Activate venv
echo "1. Activating venv..."
source venv/bin/activate || source venv/Scripts/activate

# Install Jupyter and dependencies
echo "2. Installing Jupyter and dependencies..."
pip install jupyter ipykernel matplotlib

# Create a kernel for this venv
echo "3. Creating Jupyter kernel for OptionMonger..."
python -m ipykernel install --user --name=optionmonger --display-name="OptionMonger (venv)"

echo
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo
echo "To use the notebook:"
echo "1. Run: jupyter notebook live_options_trading.ipynb"
echo "2. In Jupyter, go to Kernel > Change Kernel > OptionMonger (venv)"
echo
echo "Or start directly with the correct kernel:"
echo "jupyter notebook --kernel=optionmonger live_options_trading.ipynb"
echo "============================================================"