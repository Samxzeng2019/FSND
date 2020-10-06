#!/bin/bash
echo "run coffee shop virtual env"
. ~/workspace/venv/coffeeshop/Scripts/activate

echo "install dependencies"
cd ~/workspace/FSND/projects/03_coffee_shop_full_stack/starter_code/backend
pip install -r requirements.txt

echo "start app"
cd ~/workspace/FSND/projects/03_coffee_shop_full_stack/starter_code/backend/src
export FLASK_APP=api.py
export FLASK_ENV=development
flask run --reload
