#!/bin/bash
echo "init Fyyur env"
. ~/workspace/venv/fyyurenv/Scripts/activate

echo "install dependencies"
cd ~/workspace/FSND/projects/01_fyyur/starter_code
pip install -r requirements.txt

echo "start app"
cd ~/workspace/FSND/projects/01_fyyur/starter_code
python app.py

