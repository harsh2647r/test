from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask on Railway!"

@app.route("/api/test")
def api_test():
    return jsonify({"message": "API is working!", "status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
