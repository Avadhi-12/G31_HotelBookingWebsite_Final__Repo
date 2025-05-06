from flask import Blueprint, jsonify, request
from app import db, app
from .models import Hotel, Room, Booking, User
from datetime import datetime
from flask import url_for
from flask_cors import CORS

CORS(app)

api = Blueprint('api', __name__, url_prefix='/api')

@app.route('/api/hotels', methods=['GET', 'POST'])
def hotels():
    if request.method == 'GET':
        hotels = Hotel.query.all()
        hotel_list = []
        for h in hotels:
            hotel_data = {
                "id": h.id,
                "name": h.name,
                "location": h.location,
                "rating": h.rating,
                "description": h.description,
                "amenities": h.amenities,
                "price_per_night": str(h.price_per_night),
                "available_rooms": len(h.rooms),
                "image_url": url_for('static', filename=f'uploads/{h.image_url}', _external=True)
            }
            hotel_list.append(hotel_data)
        return jsonify(hotel_list)

    elif request.method == 'POST':
        data = request.get_json()
        new_hotel = Hotel(
            name=data['name'],
            location=data['location'],
            rating=data.get('rating', None),
            description=data.get('description', ''),
            amenities=data.get('amenities', ''),
            price_per_night=data['price_per_night'],
            image_url=data['image_url']
        )
        db.session.add(new_hotel)
        db.session.commit()
        return jsonify({"message": "Hotel added successfully!", "id": new_hotel.id}), 201


# Get rooms for a specific hotel
@api.route('/rooms/<int:hotel_id>', methods=['GET'])
def get_rooms(hotel_id):
    rooms = Room.query.filter_by(hotel_id=hotel_id).all()
    room_list = [
        {
            "id": r.id, 
            "room_type": r.room_type, 
            "price": r.price, 
            "is_available": r.is_available,
            "description": r.description
        }
        for r in rooms
    ]
    return jsonify(room_list)


# Create a booking
@api.route('/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()

    try:
        user_id = data['user_id']
        room_id = data['room_id']
        check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
        check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if room exists and is available
        room = Room.query.get(room_id)
        if not room or not room.is_available:
            return jsonify({"error": "Room not available"}), 404

        # Check for overlapping bookings
        overlapping_booking = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.check_out >= check_in,
            Booking.check_in <= check_out
        ).first()

        if overlapping_booking:
            return jsonify({"error": "Room is already booked for the selected dates."}), 400

        # Create the booking
        booking = Booking(
            user_id=user_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out
        )
        db.session.add(booking)

        # Mark the room as unavailable
        room.is_available = False
        db.session.commit()

        return jsonify({"message": "Booking created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Get a booking by ID
@api.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking:
        booking_data = {
            "id": booking.id,
            "user_id": booking.user_id,
            "room_id": booking.room_id,
            "check_in": booking.check_in,
            "check_out": booking.check_out
        }
        return jsonify(booking_data)
    else:
        return jsonify({"error": "Booking not found"}), 404


# Update booking details
@api.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    data = request.get_json()

    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        # Update booking details
        if 'check_in' in data:
            booking.check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
        if 'check_out' in data:
            booking.check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()

        db.session.commit()

        return jsonify({"message": "Booking updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Delete a booking
@api.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        # Mark room as available
        room = Room.query.get(booking.room_id)
        room.is_available = True

        db.session.delete(booking)
        db.session.commit()

        return jsonify({"message": "Booking deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



# Update hotel details
@app.route('/api/hotels/<int:id>', methods=['PUT'])
def update_hotel(id):
    hotel = Hotel.query.get_or_404(id)
    data = request.get_json()

    hotel.name = data.get('name', hotel.name)
    hotel.location = data.get('location', hotel.location)
    hotel.rating = data.get('rating', hotel.rating)
    hotel.description = data.get('description', hotel.description)
    hotel.amenities = data.get('amenities', hotel.amenities)
    hotel.price_per_night = data.get('price_per_night', hotel.price_per_night)
    hotel.image_url = data.get('image_url', hotel.image_url)

    db.session.commit()

    return jsonify({"message": "Hotel updated successfully!"})


# Delete a hotel
@api.route('/hotels/<int:hotel_id>', methods=['DELETE'])
def delete_hotel(hotel_id):
    try:
        hotel = Hotel.query.get(hotel_id)
        if not hotel:
            return jsonify({"error": "Hotel not found"}), 404

        db.session.delete(hotel)
        db.session.commit()

        return jsonify({"message": "Hotel deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Add a room
@api.route('/rooms', methods=['POST'])
def add_room():
    data = request.get_json()
    try:
        room = Room(
            hotel_id=data['hotel_id'],
            room_type=data['room_type'],
            price=data['price'],
            description=data.get('description', ''),
            is_available=True  # Default is available when added
        )
        db.session.add(room)
        db.session.commit()

        return jsonify({"message": "Room added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Update room details
@api.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    data = request.get_json()
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify({"error": "Room not found"}), 404

        room.room_type = data.get('room_type', room.room_type)
        room.price = data.get('price', room.price)
        room.description = data.get('description', room.description)
        room.is_available = data.get('is_available', room.is_available)

        db.session.commit()

        return jsonify({"message": "Room updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Delete a room
@api.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    try:
        room = Room.query.get(room_id)
        if not room:
            return jsonify({"error": "Room not found"}), 404

        db.session.delete(room)
        db.session.commit()

        return jsonify({"message": "Room deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@api.route('/api/about-us', methods=['GET'])
def about_us():
    data = {
        "title": "Welcome to BlueWave Hotels",
        "description": (
            "BlueWave Hotels is a premier hospitality brand known for comfort and elegance. "
            "Our goal is to make every guest feel at home while enjoying top-tier service, modern amenities, "
            "and beautifully designed spaces. Whether you're here for business or leisure, "
            "we're here to make your stay unforgettable."
        )
    }
    return jsonify(data)


