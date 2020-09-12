#!/bin/bash
echo "start config database"
cd ../backend

PGPASSWORD=password dropdb -U postgres trivia_test
PGPASSWORD=password createdb -U postgres trivia_test
PGPASSWORD=password psql -U postgres trivia_test < trivia.psql

echo "init api virtual env"
. ~/workspace/venv/fyyurenv/Scripts/activate

echo "install dependencies"
cd ~/workspace/FSND/projects/02_trivia_api/starter/backend
pip install -r requirements.txt

echo "start test"
python test_flaskr.py

echo "finish test"