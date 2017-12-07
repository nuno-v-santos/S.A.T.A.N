#!/bin/sh

echo "Installing requirements..."
pip install --quiet --user -r requirements.txt
export PYTHONPATH=$PWD:$PYTHONPATH
echo "Running the program..."
echo "----------------------------------------------------"
python -m satan.main
