from flask import Flask, render_template, redirect, request, url_for, flash,session,jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_login import current_user
import requests
from flask_migrate import Migrate




basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)



app.secret_key = "your_secret_key"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "Your secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    rooms = db.relationship('Room', backref='hotel', lazy=True)

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    try:
        # Step 1: Call your own Flask API
        response = requests.get("http://localhost:5000/hotels")  # Adjust port if needed
        data = response.json()

        # Step 2: Extract hotel list from response
        hotels = data.get("hotels", [])
    except Exception as e:
        print("Error fetching hotels:", e)
        hotels = []

    # Step 3: Pass the hotels list to the template
    return render_template("index.html", hotels=hotels, current_user=current_user)


@app.route("/action", methods=["POST"])
def action():
    if "user" not in session:  # Check if the user is logged in
        flash("Please register/login first", "warning")
        return redirect(url_for("index"))
    return "Performing action..."

@app.route("/check-login")
def check_login():
    return {"logged_in": "user" in session}


@app.route("/filter-hotels", methods=["POST"])
def filter_hotels():
    try:
        filters = request.json or {}
        print("Received Filters:", filters)  # Debugging output

        # Extract and convert filters safely
        max_price = int(filters.get("maxPrice", float("inf")))

        selected_stars = set(map(int, filters.get("stars", [])))
        selected_reviews = set(map(int, filters.get("reviews", [])))
        selected_rooms = set(filters.get("rooms", []))

        # Apply filters
        filtered_hotels = [
            hotel for hotel in hotels
            if hotel["price"] <= max_price
            and (not selected_stars or hotel["rating"] in selected_stars)
            and (not selected_reviews or hotel["reviews"] in selected_reviews)
            and (not selected_rooms or hotel["room_type"] in selected_rooms)
        ]

        # Sort the filtered hotels
        sort_by = filters.get("sortBy", "top_picks")
        if sort_by == "price_low":
            filtered_hotels.sort(key=lambda x: x["price"])
        elif sort_by == "best_rated":
            filtered_hotels.sort(key=lambda x: (-x["rating"], -x["reviews"]))
        elif sort_by == "nearest":
            # Placeholder for nearest logic, if available
            pass

        return jsonify({"hotels": filtered_hotels})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    
@app.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        flash("Please log in to view your dashboard.", "warning")
        return redirect(url_for("login"))

    # Query bookings for the current user
    bookings = Booking.query.filter_by(user_id=current_user.id).all()

    # Debug: Print bookings to check if the query is returning results
    print(f"Bookings for User {current_user.id}: {bookings}")

    return render_template("dashboard.html", bookings=bookings)





@app.route("/book/<int:room_id>", methods=["POST"])
def book_room(room_id):
    if not current_user.is_authenticated:  # Check if the user is logged in
        flash("Please login/register first to book a room.", "warning")
        return redirect(url_for("login"))

    room = Room.query.get_or_404(room_id)
    if not room.availability:
        flash("Room is not available.", "danger")
        return redirect(url_for("home"))

    # Retrieve check-in and check-out dates from the form
    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")

    # Create a new booking entry
    booking = Booking(user_id=current_user.id, room_id=room.id, check_in=check_in, check_out=check_out)
    
    # Update room availability to False
    room.availability = False
    
    # Add the booking to the session and commit it
    db.session.add(booking)
    db.session.commit()

    flash("Room booked successfully!", "success")
    return redirect(url_for("dashboard"))



@app.route("/hotels")
def get_hotels_data():
    all_hotels = [
        {"name": "Break & Home Paris Italie Porte de Choisy", "location": "Ivry-sur-Seine, Jaipur", "price": 7200, "image": "image1.png", "rating": 7.3, "reviews": 122, "stars": 3, "property_type": "hotel", "room_types": ["single", "double"], "facilities": ["wifi", "parking"],"available_rooms":8},
        {"name": "Le Meurice", "location": "Udaipur", "price": 15000, "image": "image2.png", "rating": 9.0, "reviews": 300, "stars": 5, "property_type": "hotel", "room_types": ["suite", "double"], "facilities": ["wifi", "spa", "parking"],"available_rooms":5},
        {"name": "Shangri-La Hotel Paris", "location": "New Delhi", "price": 18000, "image": "image3.png", "rating": 9.2, "reviews": 200, "stars": 5, "property_type": "hotel", "room_types": ["family", "suite"], "facilities": ["wifi", "pool", "spa"],"available_rooms":9},
        {"name": "Hôtel Plaza Athénée", "location": "Pune", "price": 22000, "image": "image4.png", "rating": 9.5, "reviews": 150, "stars": 5, "property_type": "hotel", "room_types": ["double", "suite"], "facilities": ["wifi", "parking", "spa", "pet"],"available_rooms":2},
        {"name": "The Peninsula Paris", "location": "New Delhi", "price": 25000, "image": "image5.png", "rating": 9.1, "reviews": 180, "stars": 5, "property_type": "hotel", "room_types": ["family", "suite"], "facilities": ["wifi", "spa", "pool", "pet"],"available_rooms":7},
        {"name": "Hotel Lutetia", "location": "Chandigarh", "price": 13000, "image": "image6.png", "rating": 8.7, "reviews": 140, "stars": 4, "property_type": "hotel", "room_types": ["single", "double"], "facilities": ["wifi", "parking"],"available_rooms":1},
        {"name": "Mandarin Oriental Paris", "location": "Jaipur", "price": 20000, "image": "image7.png", "rating": 9.3, "reviews": 210, "stars": 5, "property_type": "hotel", "room_types": ["family", "double"], "facilities": ["wifi", "spa", "parking"],"available rooms":11},
        {"name": "Citadines Les Halles Paris", "location": "Pune", "price": 9000, "image": "image8.png", "rating": 8.0, "reviews": 250, "stars": 4, "property_type": "apartment", "room_types": ["single", "double"], "facilities": ["wifi", "parking"],"available_rooms":2},
        {"name": "Residhome Paris Rosa Parks", "location": "Udaipur", "price": 6000, "image": "image9.png", "rating": 7.5, "reviews": 180, "stars": 3, "property_type": "apartment", "room_types": ["single", "family"], "facilities": ["wifi"],"available_rooms":6},
        {"name": "Four Seasons Hotel George V", "location": "Chandigarh", "price": 27000, "image": "image10.png", "rating": 9.8, "reviews": 400, "stars": 5, "property_type": "hotel", "room_types": ["suite", "double"], "facilities": ["wifi", "pool", "spa"],"available_rooms":3},
        {"name": "Les Appartements Paris Clichy", "location": "Goa", "price": 8000, "image": "image11.png", "rating": 7.9, "reviews": 130, "stars": 3, "property_type": "apartment", "room_types": ["single"], "facilities": ["wifi", "parking"],"available_rooms":19},
        {"name": "Villa Madame", "location": "Thailand", "price": 11000, "image": "image12.png", "rating": 8.5, "reviews": 160, "stars": 4, "property_type": "villa", "room_types": ["family", "suite"], "facilities": ["wifi", "parking", "spa", "pet"]},
        {"name": "La Réserve Paris Hotel and Spa", "location": "New Delhi", "price": 30000, "image": "image13.png", "rating": 9.7, "reviews": 100, "stars": 5, "property_type": "resort", "room_types": ["suite"], "facilities": ["wifi", "spa", "pool"]},
        {"name": "Novotel Paris Centre Gare Montparnasse", "location": "Udaipur", "price": 10000, "image": "image14.png", "rating": 8.2, "reviews": 200, "stars": 4, "property_type": "hotel", "room_types": ["double", "suite"], "facilities": ["wifi", "parking"]},
        {"name": "Mercure Paris Centre Tour Eiffel", "location": "Pune", "price": 12000, "image": "image15.png", "rating": 8.4, "reviews": 250, "stars": 4, "property_type": "hotel", "room_types": ["single", "double"], "facilities": ["wifi", "parking", "pet"]},
    ]

    # Get filter parameters from request
    selected_stars = request.args.getlist("star", type=int)
    max_price = request.args.get("max_price", type=int)
    property_type = request.args.get("property_type", "")
    selected_room_types = request.args.getlist("room_type")
    selected_facilities = request.args.getlist("facilities")

    # Apply filters
    filtered_hotels = all_hotels

    if selected_stars:
        filtered_hotels = [hotel for hotel in filtered_hotels if hotel["stars"] in selected_stars]

    if max_price:
        filtered_hotels = [hotel for hotel in filtered_hotels if hotel["price"] <= max_price]

    if property_type:
        filtered_hotels = [hotel for hotel in filtered_hotels if hotel["property_type"] == property_type]

    if selected_facilities:
        filtered_hotels = [hotel for hotel in filtered_hotels if all(facility in hotel["facilities"] for facility in selected_facilities)]

    if selected_room_types:
        filtered_hotels = [hotel for hotel in filtered_hotels if any(room in hotel["room_types"] for room in selected_room_types)]
    return render_template("hotels.html", hotels=filtered_hotels)


@app.route("/hotel/<int:hotel_id>")
def hotel_details(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    return render_template("hotel_details.html", hotel=hotel)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/register", methods=["GET", "POST"])
def register():
   
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        mobile = request.form.get("mobile")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, mobile=mobile, role="user")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")
    
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/availability/<hotel_name>")
def check_availability(hotel_name):
    all_hotels = [
        {"name": "Break & Home Paris Italie Porte de Choisy", "available_rooms": 8},
        {"name": "Le Meurice", "available_rooms": 5},
        {"name": "Shangri-La Hotel Paris", "available_rooms": 9},
        {"name": "Hôtel Plaza Athénée", "available_rooms": 2},
        {"name": "The Peninsula Paris", "available_rooms": 7},
        {"name": "Hotel Lutetia", "available_rooms": 1},
        {"name": "Mandarin Oriental Paris", "available_rooms": 2}
    ]
    
    # Find the hotel
    hotel = next((h for h in all_hotels if h["name"] == hotel_name), None)
    
    if hotel:
        return {"available_rooms": hotel["available_rooms"]}
    else:
        return {"error": "Hotel not found"}, 404
    
@app.route('/booking')
@login_required
def booking():
    hotel_id = request.args.get('hotel_id')
    hotel = Hotel.query.get(hotel_id)
    room = Room.query.filter_by(hotel_id=hotel_id).first()

    if not hotel or not room:
        flash("Hotel or Room not found!", "danger")
        return redirect(url_for('index'))

    return render_template("booking.html", hotel=hotel, room=room)


@app.route('/confirm_booking', methods=['POST'])
@login_required
def confirm_booking():
    hotel_id = request.form.get('hotel_id')
    room_id = request.form.get('room_id')
    
    booking = Booking(user_id=current_user.id, hotel_id=hotel_id, room_id=room_id)
    db.session.add(booking)
    db.session.commit()
    
    flash("Booking Confirmed! 🎉", "success")
    return redirect(url_for('index'))


@app.route('/payment')
def payment():
    return render_template('payment.html')



@app.route('/process_payment', methods=['POST'])
def process_payment():
    hotel_name = request.form.get('hotel_name')
    price = request.form.get('price')

    # Simulate payment processing (replace with real payment API)
    if request.form.get('card_number') and request.form.get('cvv'):
        flash(f'Payment successful for {hotel_name} (₹{price})!', 'success')
        return redirect(url_for('hotels'))  # Redirect to hotels page after payment
    else:
        flash('Payment failed. Please try again.', 'danger')
        return redirect(url_for('payment'))
    


@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route("/add_hotel", methods=["GET", "POST"])
def add_hotel():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        description = request.form["description"]

        new_hotel = Hotel(name=name, location=location, description=description)
        db.session.add(new_hotel)
        db.session.commit()
        flash("Hotel added successfully!", "success")
        return redirect(url_for("home"))
    
    return render_template("add_hotel.html")




@app.route('/hotels/<int:id>', methods=['PUT'])
def update_hotel(id):
    hotel = Hotel.query.get_or_404(id)
    data = request.get_json()
    if 'name' in data:
        hotel.name = data['name']
    if 'city' in data:
        hotel.city = data['city']
    if 'price' in data:
        hotel.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Hotel updated successfully'}), 200



@app.route("/delete_hotel/<int:hotel_id>", methods=["POST"])
def delete_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    db.session.delete(hotel)
    db.session.commit()
    flash("Hotel deleted successfully!", "success")
    return redirect(url_for("home"))



@app.route("/add_room", methods=["GET", "POST"])
def add_room():
    if request.method == "POST":
        hotel_id = request.form["hotel_id"]
        room_type = request.form["room_type"]
        price = request.form["price"]
        availability = bool(request.form.get("availability"))

        new_room = Room(hotel_id=hotel_id, room_type=room_type, price=price, availability=availability)
        db.session.add(new_room)
        db.session.commit()
        flash("Room added successfully!", "success")
        return redirect(url_for("home"))
    
    hotels = Hotel.query.all()  # Get all hotels to display in a dropdown
    return render_template("add_room.html", hotels=hotels)




@app.route("/update_room/<int:room_id>", methods=["GET", "POST"])
def update_room(room_id):
    room = Room.query.get_or_404(room_id)

    if request.method == "POST":
        room.room_type = request.form["room_type"]
        room.price = request.form["price"]
        room.availability = bool(request.form.get("availability"))

        db.session.commit()
        flash("Room updated successfully!", "success")
        return redirect(url_for("home"))

    hotels = Hotel.query.all()  # Get all hotels to display in a dropdown
    return render_template("update_room.html", room=room, hotels=hotels)




@app.route("/delete_room/<int:room_id>", methods=["POST"])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted successfully!", "success")
    return redirect(url_for("home"))



@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    print("🔍 Flask received JSON:", data)  # Debug

    # Make sure all required keys are present
    required = ['username', 'email', 'password', 'mobile', 'role']
    missing = set(required) - set(data.keys())
    if missing:
        return jsonify({"error": f"Missing field(s): {missing}"}), 400

    try:
        # Map 'username' ⇒ model.name, drop 'age' (unless you add it to your model)
        new_user = User(
            name=data['username'],                # model expects 'name'
            email=data['email'],
            mobile=data['mobile'],
            role=data.get('role', 'user')         # use get() for default
        )
        new_user.set_password(data['password'])   # hashes into password_hash

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User added successfully"}), 201

    except Exception as e:
        print("❌ Error creating user:", e)
        return jsonify({"error": str(e)}), 400




from api.rooms import api as api_blueprint
app.register_blueprint(api_blueprint)


from api.bookings import api as bookings_blueprint
app.register_blueprint(bookings_blueprint)

from api.hotels import api as hotels_blueprint
app.register_blueprint(hotels_blueprint)

from api.users import api as users_blueprint
app.register_blueprint(users_blueprint)



@app.route('/api/about-us', methods=['GET'])
def about_us():
    data = {
        "title": "Where Every Detail is a Masterpiece",
        "description": (
            "BlueWave Hotels is a premier hospitality brand known for comfort and elegance. "
            "Our goal is to make every guest feel at home while enjoying top-tier service, modern amenities, "
            "and beautifully designed spaces. Whether you're here for business or leisure, "
            "we're here to make your stay unforgettable."
        )
    }
    return jsonify(data)

@app.route('/api/team', methods=['GET'])
def get_team():
    team_data = [
        {"name": "Avadhi", "role": "Admin", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRd0en53aSgl3-U4J5ukwTCFhP8e2TJrXaJSw&s"},
        {"name": "Ansh", "role": "Admin", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoJdwFalgenF9tl3xM6xvw6WX5FsIK-vKM1w&s"},
        {"name": "Aashna", "role": "User", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRd0en53aSgl3-U4J5ukwTCFhP8e2TJrXaJSw&s"},
        {"name": "Bhuvnesh", "role": "User", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoJdwFalgenF9tl3xM6xvw6WX5FsIK-vKM1w&s"},
    ]
    return jsonify(team_data)



if __name__ == "__main__":
    app.run(debug=True) 