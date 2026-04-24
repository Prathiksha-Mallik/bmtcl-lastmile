from flask import Blueprint, request, jsonify
from services.logic import get_best_option

api = Blueprint("api", __name__)

@api.route("/get_places", methods=["GET", "POST"])
def get_places():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        station = data.get("station")
        destination = data.get("destination")
    else:
        station = request.args.get("station")
        destination = request.args.get("destination")

    if not station or not destination:
        return jsonify({"error": "Station and destination are required"}), 400

    result = get_best_option(station, destination)

    return jsonify(result)
