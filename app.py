from flask import Flask
from routes.api import api   # your blueprint

app = Flask(__name__)

# ✅ Home route (fixes 404 error)
@app.route('/')
def home():
    return "Backend is running 🚀"

# ✅ Register your API routes
app.register_blueprint(api)

# ✅ Run server
if __name__ == "__main__":
    app.run(debug=True)