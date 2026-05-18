from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route("/test", methods=["POST"])
def test():
    return {"hello": "world"}
