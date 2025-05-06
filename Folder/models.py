# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from app import db, bcrypt
from flask_login import UserMixin
from app import login_manager

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    # ✅ Define relationship using back_populates
    bookings = db.relationship('Booking', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    
    rating = db.Column(db.Float, nullable=False, default=3.5)

    amenities = db.Column(db.String(255), nullable=True)  # e.g., "WiFi,Parking"
    room_type = db.Column(db.String(20), nullable=True)   # e.g., "Single", "Double", "Suite"
    property_type = db.Column(db.String(50), nullable=True)  # e.g., "Hotel", "Villa", etc.

    available_rooms = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)  # Store full image URL

    rooms = db.relationship('Room', backref='hotel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'rating': self.rating,
            'amenities': self.amenities,
            'price': float(self.price_per_night) if self.price_per_night else None,
            'room_type': self.room_type,
            'property_type': self.property_type,
            'available_rooms': self.available_rooms,
            'image_url': self.image_url
        }


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)

    # ✅ Matching back_populates relationship
    user = db.relationship('User', back_populates='bookings')
    room = db.relationship('Room')
