from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from SkipScrapper import sd_home_scrape
from DDscraper import dd_scrape
from UEscraper import ue_scrape

# Setup the server
app = Flask(__name__)

# Setup the database for the server
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/skip', methods=['POST'])
def sd():
    addr = request.form['address']
    food = request.form['food']

    d = {}
    rests_lst = sd_home_scrape(addr, food, 10)
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        d[f"rest_{i}"] = rest.d_json

    return jsonify(d)

@app.route('/dash', methods=['POST'])
def dd():
    addr = request.form['address']
    food = request.form['food']

    d = {}
    rests_lst = dd_scrape(addr, food, 10)
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        d[f"rest_{i}"] = rest.d_json

    return jsonify(d)

@app.route('/eats', methods=['POST'])
def ue():
    addr = request.form['address']
    food = request.form['food']

    d = {}
    rests_lst = ue_scrape(addr, food, 10)
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        d[f"rest_{i}"] = rest.d_json

    return jsonify(d)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

    # It's already preset to run this html doc on a local server
    app.run(debug=True)