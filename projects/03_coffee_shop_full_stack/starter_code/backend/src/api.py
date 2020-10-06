import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()


# ROUTES
@app.route('/drinks', methods=['GET'])
def list_drinks():
    drinks = Drink.query.all()
    drinks_short = []
    for drink in drinks:
        drinks_short.append(drink.short())

    return jsonify({
        'success': True,
        'drinks': drinks_short
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.order_by(Drink.id).all()
    drinks_long = []
    for drink in drinks:
        drinks_long.append(drink.long())

    return jsonify({
        'success': True,
        'drinks': drinks_long
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')

    drink = Drink(
        title=new_title,
        recipe=json.dumps(new_recipe)
    )
    try:
        drink.insert()
    except Exception as e:
        print(e)
        abort(422)

    current_drink = Drink.query.filter_by(title=new_title).first()

    if not current_drink:
        abort(400)
    return jsonify({
        'success': True,
        'drinks': [current_drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drinks(payload, drink_id):
    body = request.get_json()
    if not drink_id:
        abort(404)
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if body.get('title'):
        drink.title = body.get('title')
    if body.get('recipe'):
        drink.recipe = body.get('recipe')
    try:
        drink.update()
    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['Delete'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    if not drink_id:
        abort(404)
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    try:
        drink.delete()
    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
        'success': True,
        'delete': drink.id
    })                                                              


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def resource_not_found(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "authentication error"
    }), 401
