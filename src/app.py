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
from models import db, User, Character, Planet, Favorite
#from models import Person

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# get characters
@app.route("/characters",  methods=['GET'])
def get_characters():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters])

# get one character
@app.route("/characters/<int:characters_id>", methods=['GET'])
def get_one_character(characters_id):
    character = Character.query.get(characters_id)
    return jsonify(character.serialize()) if character else jsonify({"error": "Character not found"}), 404

# get planets
@app.route("/planets",  methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets])
# get one planet
@app.route("/planets/<int:planets_id>", methods=['GET'])
def get_one_planet(planets_id):
    planet = Planet.query.get(planets_id)
    return jsonify(planet.serialize()) if planet else jsonify({"error": "Planet not found"}), 404
# get users
@app.route("/users",  methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])
# get user favorites
@app.route("/users/favorites",  methods=['GET'])
def get_user_favorites():
    user_id = 1
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify([favorite.serialize() for favorite in user.favorites])
# add favorite planet
@app.route("/favorites/planet/<int:planet_id>", methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg":"Planet added to favorites"})
# add favorite character
@app.route("/favorites/character/<int:character_id>", methods=['POST'])
def add_favorite_character(character_id):
    user_id = 1
    favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg":"Character added to favorites"})
# delete favorite planet
@app.route("/favorites/planet/<int:planet_id>", methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg":"Planet removed from favorites"})

# delete favorite CHARACTER
@app.route("/favorites/character/<int:character_id>", methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg":"Character removed from favorites"})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
