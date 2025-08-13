#!/bin/bash

echo "========================================"
echo "OptionMonger Setup Script"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ Pip upgraded"

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt --quiet
echo "✓ Requirements installed"

# Check if .env exists
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "IMPORTANT: Please edit .env file with your TWS settings:"
    echo "  - Set TWS_HOST (default: 127.0.0.1)"
    echo "  - Set TWS_PAPER_PORT (default: 7497 for paper trading)"
    echo "  - Set TWS_LIVE_PORT (default: 7496 for live trading)"
    echo "  - Set USE_PAPER_TRADING (default: true)"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To use the application:"
echo "  1. Make sure TWS or IB Gateway is running"
echo "  2. Enable API access in TWS settings"
echo "  3. Run commands using:"
echo "     ./run.sh stock AAPL"
echo "     ./run.sh chain AAPL"
echo "     ./run.sh greeks AAPL -e 20240419 -s 150 -t C"
echo ""
echo "Or activate the virtual environment manually:"
echo "     source venv/bin/activate"
echo "     python main.py --help"