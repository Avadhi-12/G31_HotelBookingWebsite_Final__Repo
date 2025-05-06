from flask import Blueprint, jsonify
from app import db, Hotel

api = Blueprint('hotel_api', __name__, url_prefix='/api')

@api.route('/hotels', methods=['GET'])
def get_hotels():
    hotels = Hotel.query.all()
    hotel_list = [
        {
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "description": hotel.description
        }
        for hotel in hotels
    ]
    return jsonify(hotel_list)
