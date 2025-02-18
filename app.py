# app.py
from flask import Flask, render_template, request, jsonify
from src.routes import evaluation_bp, ui_route_bp
from config import Config
config = Config()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

app.register_blueprint(ui_route_bp, url_prefix='/ui')
app.register_blueprint(evaluation_bp, url_prefix='/evaluation')



if __name__ == "__main__":
    app.run(debug=True)
