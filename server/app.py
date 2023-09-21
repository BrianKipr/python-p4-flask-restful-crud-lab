#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)

api.add_resource(Plants, '/plants')

class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)

api.add_resource(PlantByID, '/plants/<int:id>')

@app.route('/plants/<int:id>', methods=['PATCH'])
def update_plant(id):
    # Get the plant by ID from the database
    plant = Plant.query.get_or_404(id)

    # Update the plant's attributes based on the request JSON data
    data = request.get_json()
    if 'is_in_stock' in data:
        plant.is_in_stock = data['is_in_stock']

    # Commit the changes to the database
    db.session.commit()

    # Return the updated plant as JSON response
    return jsonify({
        'id': plant.id,
        'name': plant.name,
        'image': plant.image,
        'price': float(plant.price),  # Convert Decimal to float for JSON
        'is_in_stock': plant.is_in_stock
    })

if __name__ == '__main__':
    app.run(port=5555, debug=True)
