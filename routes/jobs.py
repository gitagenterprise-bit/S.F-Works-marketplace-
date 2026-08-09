from flask import Blueprint, jsonify


jobs_bp = Blueprint(
    "jobs",
    __name__
)


@jobs_bp.route(
    "/",
    methods=["GET"]
)
def jobs():

    return jsonify({
        "status": "success",
        "message": "Public jobs endpoint"
    })
