from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

places = {
     "hhitefield (kadugodi)": ["Phoenix Marketcity", "VR Bengaluru", "ITPL Food Court"],
    "kr puram": ["Orion Uptown Mall", "Lake View Shops", "Food Court"],
    "indiranagar": ["100ft Road Cafes", "Toit Brewery", "Nike Store"],
    "mg road": ["UB City Mall", "Brigade Road", "Church Street Cafes"],
    "trinity": ["MG Road Shops", "Brigade Road", "Restaurants"],
    "cubbon park": ["Museum Cafes", "High Court Area Shops"],
    "vidhana soudha": ["Government Area Cafes", "Book Stalls"],
    "majestic": ["City Market", "Railway Shops", "Bus Stand Shops"],
    "magadi road": ["Local Shops", "Food Stalls"],
    "vijayanagar": ["Bangalore Central Mall", "Local Market", "Restaurants"],
    "attiguppe": ["Metro Shops", "Local Cafes"],
    "mysuru road": ["Bus Stand Shops", "Local Market"],
    "kengeri": ["Global Mall", "Food Street", "Local Shops"],
    "nayandahalli": ["RR Nagar Mall", "Food Court"],
    "rajajinagar": ["Orion Mall", "Rajajinagar Market"],
    "peenya": ["Industrial Shops", "Food Stalls"],
    "dasarahalli": ["Local Shops", "Tea Stalls"],
    "nagasandra": ["Small Market", "Local Shops"],
    "yeshwanthpur": ["Orion Mall", "Railway Shops"],
    "sandal soap factory": ["Industrial Area Shops", "Food Stalls"],
    "mahalakshmi": ["Mall Area Shops", "Cafes"],
    "srirampura": ["Street Shops", "Food Stalls"],
    "mantri square": ["Mantri Mall", "Food Court"],
    "chickpet": ["Textile Shops", "Wholesale Market"],
    "kr market": ["Flower Market", "Spice Market"],
    "national college": ["Book Stores", "Cafes"],
    "lalbagh": ["Garden Cafes", "Plant Shops"],
    "south end circle": ["Jayanagar Shops", "Cafes"],
    "jayanagar": ["4th Block Market", "Shopping Complex"],
    "banashankari": ["Big Bazaar", "Food Street"],
    "yelachenahalli": ["Local Shops", "Food Corner"],
    "silk institute": ["College Cafes", "Small Shops"]
}
    

@app.route('/')
def home():
    return "Backend is running 🚀"

@app.route('/get_places')
def get_places():
    station = request.args.get('station', '').lower()

    return jsonify({
        "station": station,
        "nearby_places": places.get(station, ["No data available"]),
        "walking_time": "6 mins",
        "bus_waiting_time": "10 mins",
        "auto": "Yes",
        "suggestion": "Walk 🚶"
    })

if __name__ == "__main__":
    app.run(debug=True)