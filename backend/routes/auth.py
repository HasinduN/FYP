from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token, get_jwt_identity
from models import session, User, TokenBlockList
import datetime
from functools import wraps

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Fetch the currently authenticated user's details"""
    try:
        identity = get_jwt_identity()  # Extract JWT identity

        if not identity:
            return jsonify({"error": "Invalid token"}), 401  # Token issue

        user = session.query(User).filter_by(id=int(identity)).first()  # Convert identity to int
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"id": user.id, "username": user.username, "role": user.role}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user with unique username and email"""
    data = request.json

    try:
        # Check if the username already exists
        existing_username = session.query(User).filter_by(username=data["username"]).first()
        if existing_username:
            return jsonify({"message": "Username already exists!"}), 400

        # Check if the email already exists
        existing_email = session.query(User).filter_by(email=data["email"]).first()
        if existing_email:
            return jsonify({"message": "Email already exists!"}), 400

        # Create new user
        new_user = User(username=data["username"], email=data["email"], role=data["role"])
        new_user.set_password(data["password"])

        session.add(new_user)
        session.commit()

        return jsonify({"message": "User registered successfully!"}), 201

    except Exception as e:
        session.rollback()
        print(f"Error registering user: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token using username instead of email"""
    data = request.json
    user = session.query(User).filter_by(username=data["username"]).first()  # Use username

    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials!"}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({"token": access_token, "role": user.role}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Blacklist the current JWT token on logout"""
    try:
        jti = get_jwt()["jti"]
        now = datetime.datetime.utcnow()

        if session.query(TokenBlockList).filter_by(jti=jti).first():
            return jsonify({"message": "Token is already blacklisted"}), 400

        session.add(TokenBlockList(jti=jti, created_at=now))
        session.commit()

        return jsonify({"message": "Logged out successfully!"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route("/update-profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update user's username and password"""
    user_id = get_jwt_identity()
    data = request.json

    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if "username" in data:
        user.username = data["username"]

    if "password" in data and data["password"]:
        user.set_password(data["password"])

    session.commit()
    return jsonify({"message": "Profile updated successfully!"}), 200