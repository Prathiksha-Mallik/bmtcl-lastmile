from flask import Blueprint, request, jsonify
from services.logic import get_best_option

api = Blueprint('api', __name__)

@api.route('/recommend', methods=['GET'])
def recommend():
    station = request.args.get('station')
    destination = request.args.get('destination')

    result = get_best_option(station, destination)

    return jsonify(result)