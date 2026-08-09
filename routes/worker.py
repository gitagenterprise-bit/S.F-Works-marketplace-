from flask import Blueprint, jsonify

from utils.decorators import role_required


worker_bp = Blueprint(
    "worker",
    __name__
)


@worker_bp.route(
    "/dashboard",
    methods=["GET"]
)
@role_required("worker")
def dashboard():

    return jsonify({
        "status": "success",
        "message": "Welcome to Worker Dashboard",
        "role": "worker"
    })
