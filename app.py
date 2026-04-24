from flask import Flask
from flask_cors import CORS

from routes.api import api

app = Flask(__name__)
CORS(app)

app.register_blueprint(api)


@app.route("/")
def home():
    return "Backend is running"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
