from flask import jsonify


def success_response(
    message="Success",
    data=None,
    status_code=200
):

    return jsonify({

        "status": "success",

        "message":
            message,

        "data":
            data

    }), status_code


def error_response(
    message="Something went wrong",
    status_code=400,
    errors=None
):

    response = {

        "status": "error",

        "message":
            message

    }

    if errors is not None:

        response["errors"] = errors

    return jsonify(
        response
    ), status_code
