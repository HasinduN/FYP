from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint("auth", __name__)

# ✅ User Registration
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "cashier")  # Default role is "cashier"

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        # Create new user
        new_user = User(username=username, role=role)
        new_user.set_password(password)  # Hash password

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ✅ User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"access_token": access_token, "role": user.role}), 200
