import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

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


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# Get all people
@app.route("/people", methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([person.serialize() for person in people])

# Get one person
@app.route("/people/<int:people_id>", methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize())
    else:
        return jsonify({"error": "Person not found"}), 404

# Get all planets
@app.route("/planets", methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets])

# Get one planet
@app.route("/planets/<int:planet_id>", methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize())
    else:
        return jsonify({"error": "Planet not found"}), 404

# Get all users
@app.route("/users", methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

# Get user favorites
@app.route("/users/favorites", methods=['GET'])
def get_user_favorites():
    user_id = 1  
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify([favorite.serialize() for favorite in user.favorites])

# Add favorite planet
@app.route("/favorite/planet/<int:planet_id>", methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1  
    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites"})

# Add favorite people
@app.route("/favorite/people/<int:people_id>", methods=['POST'])
def add_favorite_people(people_id):
    user_id = 1  
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Person added to favorites"})

# Delete favorite planet
@app.route("/favorite/planet/<int:planet_id>", methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planet removed from favorites"})

# Delete favorite people
@app.route("/favorite/people/<int:people_id>", methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = 1  
    favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Person removed from favorites"})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
