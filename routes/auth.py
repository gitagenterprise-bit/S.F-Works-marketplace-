from flask import Blueprint, request, jsonify, render_template

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from sqlalchemy import or_

from extensions import db
from models.user import User
from models.customer import CustomerProfile
from models import WorkerProfile


auth_bp = Blueprint(
    "auth",
    __name__
)


@app.route("/login")
def login_page():
    return render_template("auth/login.html")


@app.route("/register")
def register_page():
    return render_template("auth/register.html")


@auth_bp.route(
    "/register/customer",
    methods=["POST"]
)
def register_customer():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body is required"
        }), 400

    full_name = data.get("full_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not full_name:
        return jsonify({
            "status": "error",
            "message": "Full name is required"
        }), 400

    if not email:
        return jsonify({
            "status": "error",
            "message": "Email is required"
        }), 400

    if not phone:
        return jsonify({
            "status": "error",
            "message": "Phone is required"
        }), 400

    if not password:
        return jsonify({
            "status": "error",
            "message": "Password is required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must be at least 8 characters"
        }), 400

    existing_user = User.query.filter(
        or_(
            User.email == email,
            User.phone == phone
        )
    ).first()

    if existing_user:

        return jsonify({
            "status": "error",
            "message": "Email or phone already registered"
        }), 409

    user = User(
        full_name=full_name.strip(),
        email=email.lower().strip(),
        phone=phone.strip(),
        role="customer"
    )

    user.set_password(password)

    db.session.add(user)

    db.session.flush()

    profile = CustomerProfile(
        user_id=user.id
    )

    db.session.add(profile)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Customer registration successful",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }), 201

@auth_bp.route(
    "/register/worker",
    methods=["POST"]
)
def register_worker():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body is required"
        }), 400

    full_name = data.get("full_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    profession = data.get("profession")

    if not full_name:
        return jsonify({
            "status": "error",
            "message": "Full name is required"
        }), 400

    if not email:
        return jsonify({
            "status": "error",
            "message": "Email is required"
        }), 400

    if not phone:
        return jsonify({
            "status": "error",
            "message": "Phone is required"
        }), 400

    if not password:
        return jsonify({
            "status": "error",
            "message": "Password is required"
        }), 400

    if not profession:
        return jsonify({
            "status": "error",
            "message": "Profession is required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must be at least 8 characters"
        }), 400

    existing_user = User.query.filter(
        or_(
            User.email == email,
            User.phone == phone
        )
    ).first()

    if existing_user:

        return jsonify({
            "status": "error",
            "message": "Email or phone already registered"
        }), 409

    user = User(
        full_name=full_name.strip(),
        email=email.lower().strip(),
        phone=phone.strip(),
        role="worker"
    )

    user.set_password(password)

    db.session.add(user)

    db.session.flush()

    worker_profile = WorkerProfile(
        user_id=user.id,
        profession=profession.strip()
    )

    db.session.add(worker_profile)

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Worker registration successful",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        },
        "worker_profile": {
            "profession": worker_profile.profession,
            "verification_status":
                worker_profile.verification_status
        }
    }), 201

@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(
        email=email.lower().strip()
    ).first()

    if not user:

        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    if not user.check_password(password):

        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    if not user.is_active:

        return jsonify({
            "status": "error",
            "message": "Your account has been disabled"
        }), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_verified": user.is_verified
        }
    }), 200

@auth_bp.route(
    "/me",
    methods=["GET"]
)
@jwt_required()
def current_user():

    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        int(user_id)
    )

    if not user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    response = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "profile_image": user.profile_image,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat()
    }

    if user.role == "customer" and user.customer_profile:

        profile = user.customer_profile

        response["profile"] = {
            "city": profile.city,
            "state": profile.state,
            "pincode": profile.pincode,
            "address": profile.address,
            "bio": profile.bio
        }

    elif user.role == "worker" and user.worker_profile:

        profile = user.worker_profile

        response["profile"] = {
            "profession": profile.profession,
            "experience_years":
                profile.experience_years,
            "service_area":
                profile.service_area,
            "hourly_rate":
                float(profile.hourly_rate)
                if profile.hourly_rate
                else None,
            "city": profile.city,
            "state": profile.state,
            "pincode": profile.pincode,
            "rating":
                float(profile.rating)
                if profile.rating
                else 0,
            "total_reviews":
                profile.total_reviews,
            "total_jobs":
                profile.total_jobs,
            "is_available":
                profile.is_available,
            "verification_status":
                profile.verification_status
        }

    return jsonify({
        "status": "success",
        "user": response
    }), 200

@auth_bp.route(
    "/refresh",
    methods=["POST"]
)
@jwt_required(
    refresh=True
)
def refresh():

    user_id = get_jwt_identity()

    user = db.session.get(
        User,
        int(user_id)
    )

    if not user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    if not user.is_active:

        return jsonify({
            "status": "error",
            "message": "Account is disabled"
        }), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return jsonify({
        "status": "success",
        "access_token": access_token
    }), 200


