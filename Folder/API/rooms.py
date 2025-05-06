from flask import Blueprint, jsonify
from app import db, Room  # Import db and Room model from app.py

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    room_list = [
        {
            "id": room.id,
            "hotel_id": room.hotel_id,
            "room_type": room.room_type,
            "price": room.price,
            "availability": room.availability
        }
        for room in rooms
    ]
    return jsonify(room_list)
