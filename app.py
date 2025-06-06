from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from AI Resume on Railway!"


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))  # Railway assigns the PORT dynamically
    app.run(host="0.0.0.0", port=port)
