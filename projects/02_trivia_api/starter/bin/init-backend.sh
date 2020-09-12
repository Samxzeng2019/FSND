#!/bin/bash
echo "init api virtual env"
. ~/workspace/venv/fyyurenv/Scripts/activate

echo "install dependencies"
cd ~/workspace/FSND/projects/02_trivia_api/starter/backend
pip install -r requirements.txt

echo "start app"
cd ~/workspace/FSND/projects/02_trivia_api/starter/backend
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run

# python app.py

