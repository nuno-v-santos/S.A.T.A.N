#!/bin/sh

echo "Installing requirements..."
pip install --user -r requirements.txt
export PYTHONPATH=$PWD:$PYTHONPATH
echo "Running the program..."
echo "----------------------------------------------------"
python -m satan.main
