import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

import collections
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def getDrinks():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)
    drinkList = []
    for drink in drinks:
        drinkList.append(drink.short())
    print(drinkList)
    return jsonify({
        "success": True,
        "drinks": drinkList
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getDrinksDetails():
    print('reached')
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)
    drinkList = []
    for drink in drinks:
        drinkList.append(drink.long())
    print(drinkList)
    return jsonify({
        "success": True,
        "drinks": drinkList
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def postDrink():
    drinks = Drink.query.all()
    titles = []
    for drink in drinks:
        titles.append(drink.title)
    content = request.get_json()
    newDrinkTitle = content.get('title', None)
    newDrinkRecipe = json.dumps(content.get('recipe', None))
    print(newDrinkRecipe)
    if newDrinkTitle not in titles:
        newDrink = Drink(title=newDrinkTitle, recipe=newDrinkRecipe)
        newDrink.insert()
    else:
        raise Exception('drink already exists')
    return jsonify({
        "success": True,
        "drinks": [newDrinkTitle, newDrinkRecipe]
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def updateDrink(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    content = request.get_json()
    print(content)
    drink.title = content.get('title', None)
    drink.recipe = json.dumps(content.get('recipe', None))
    drink.update()
    return jsonify({
        "success": True,
        "drinks":  [drink.title, drink.recipe]
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrink(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Content unprocessable"
    }), 422


@app.errorhandler(AuthError)
def authError(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": AuthError.error
    }), 403
