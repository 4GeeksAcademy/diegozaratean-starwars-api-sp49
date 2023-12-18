"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Ciudad
#from models import Person
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "clavejose"  # Change this!  abc  ttyrtyasdfajsofiuhajsudfhakjsdhfkjashdfjkhaksjdfhk
# clavejose
# abc. abcclavejose
# 123 123clavejose
# qfg qfgcclavejose
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# INCIO DE CODIGO 
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "Bad email "}), 401
    
    print(user)
    print(user.serialize())
    print(user.password)

    if user.password != password:
        return jsonify({"msg": "Bad password "}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    all_users = User.query.all()
    print(all_users)
    results = list(map(lambda user: user.serialize() ,all_users))
    print(results)


    response_body = {
        "msg": "debo leer todos los usuarios "
    }

    return jsonify(results), 200

@app.route('/ciudad', methods=['GET'])
def get_ciudades():
    all_ciudades = Ciudad.query.all()
    results = list(map(lambda item: item.serialize() ,all_ciudades))    

    return jsonify(results), 200

@app.route('/ciudad/<int:ciudad_id>', methods=['GET'])
def get_ciudad(ciudad_id):
    print(ciudad_id)
    ciudad = Ciudad.query.filter_by(id=ciudad_id).first()
    print(ciudad)
    all_ciudades = Ciudad.query.all()
    results = list(map(lambda item: item.serialize() ,all_ciudades))    

    return jsonify(ciudad.serialize()), 200

@app.route('/ciudad', methods=['POST'])
def crear_ciudad():
    print('hola terminal')
    # tarer los datos del post 
    print(request)
    print(request.get_json())
    print(request.get_json()['nombre'])
    nombre_ciudad = request.get_json()['nombre']
    body = request.get_json()
    # crear una ciudad en la bd
    ciudad = Ciudad(**body)
    # ciudad = Ciudad(nombre=body['nombre'],bandera=body['bandera'],himno=body['himno'] )
    db.session.add(ciudad)
    db.session.commit()
    response_body = {
        "msg": "debo crear ciudad"
    }

    return jsonify(response_body), 200
# FIN DE CODIGO 

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
