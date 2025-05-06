from flask import Blueprint, jsonify
from app import db, User

api = Blueprint('user_api', __name__, url_prefix='/api')

@api.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "role": user.role
        }
        for user in users
    ]
    return jsonify(user_list)

@api.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile,
        "role": user.role
    }
    return jsonify(user_data)
