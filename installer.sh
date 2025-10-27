#!/bin/bash

echo "========================================"
echo "DAEMON NETWORK INSTALLER"
echo "========================================"
echo ""

PYTHON_VERSION="python3"
VENV_NAME="daemon_venv"

if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.11 or later from https://www.python.org/"
    exit 1
fi

PYTHON_VER=$($PYTHON_VERSION --version 2>&1 | awk '{print $2}')
echo "Detected Python version: $PYTHON_VER"
echo ""

if [ -d "$VENV_NAME" ]; then
    echo "Virtual environment already exists. Removing..."
    rm -rf "$VENV_NAME"
fi

echo "Creating virtual environment: $VENV_NAME"
$PYTHON_VERSION -m venv "$VENV_NAME"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

echo "Activating virtual environment..."
source "$VENV_NAME/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip --quiet

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "========================================"
echo "INSTALLATION COMPLETE"
echo "========================================"
echo ""
echo "To launch the Daemon Network system:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source $VENV_NAME/bin/activate"
echo ""
echo "2. Start the web interface:"
echo "   python web_interface.py"
echo ""
echo "3. Open your browser and navigate to:"
echo "   http://localhost:5000"
echo ""
echo "4. To run the daemon core separately:"
echo "   python daemon_core.py"
echo ""
echo "To deactivate the virtual environment when done:"
echo "   deactivate"
echo ""
echo "========================================"
