from flask import Blueprint, jsonify
from app import db, Booking

api = Blueprint('booking_api', __name__, url_prefix='/api')

@api.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    booking_list = [
        {
            "id": booking.id,
            "user_id": booking.user_id,
            "room_id": booking.room_id,
            "check_in": booking.check_in.isoformat(),
            "check_out": booking.check_out.isoformat()
        }
        for booking in bookings
    ]
    return jsonify(booking_list)

@api.route('/bookings/<int:id>', methods=['GET'])
def get_booking_by_id(id):
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    booking_data = {
        "id": booking.id,
        "user_id": booking.user_id,
        "room_id": booking.room_id,
        "check_in": booking.check_in.isoformat(),
        "check_out": booking.check_out.isoformat()
    }
    return jsonify(booking_data)
