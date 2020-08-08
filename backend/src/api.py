import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = []
    for drink in drinks:
        formatted_drinks.append(drink.short())
    response = {
        "success": True,
        "drinks": formatted_drinks
    }
    return jsonify(response)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    formatted_drinks = []
    for drink in drinks:
        formatted_drinks.append(drink.long())
    response = {
        "success": True,
        "drinks": formatted_drinks
    }
    return jsonify(response)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    if "title" not in request.get_json() or request.get_json()["title"] == "" or "recipe" not in request.get_json() or request.get_json()["recipe"] == "":
        abort(400)
    drink = Drink(title=request.get_json()[
                  "title"], recipe=json.dumps(request.get_json()["recipe"]))
    drink.insert()
    response = {
        "success": True,
        "drinks": [drink.short()]
    }
    return jsonify(response)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    if "title" not in request.get_json() or request.get_json()["title"] == "" or "recipe" not in request.get_json() or request.get_json()["recipe"] == "":
        abort(400)
    drink.title = request.get_json()["title"]
    drink.recipe = json.dumps(request.get_json()["recipe"])
    drink.update()

    response = {
        "success": True,
        "drinks": [drink.long()]
    }
    return jsonify(response)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()
    response = {
        "success": True,
        "delete": id
    }

    return jsonify(response)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@ app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@ app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found."
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@ app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized Access."
    }), 401


@ app.errorhandler(500)
def internal(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error."
    }), 500
