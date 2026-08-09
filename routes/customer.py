from flask import Blueprint, jsonify

from utils.decorators import role_required


customer_bp = Blueprint(
    "customer",
    __name__
)


@customer_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("customer")
def dashboard():

    return jsonify({
        "status": "success",
        "message": "Welcome to Customer Dashboard",
        "role": "customer"
    })
