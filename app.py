from flask import Flask, render_template, jsonify
from flask import request as r

from SkipScrapper import sd_home_scrape
from DDscraper import dd_scrape
from UEscraper import ue_scrape


app = Flask(__name__)

@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/skip', methods=['POST'])
def sd():
    addr = r.form['address']
    food = r.form['food']

    d = {"rests":[]}
    rests_lst = sd_home_scrape(addr, food, 2)
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        d["rests"].append(rest.d_json)
    print(d)
    return jsonify(d)

@app.route('/dash', methods=['POST'])
def dd():
    addr = r.form['address']
    food = r.form['food']

    d = {"rests":[]}
    rests_lst = dd_scrape(addr, food, 10)
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        d["rests"].append(rest.d_json)
    return jsonify(d)

@app.route('/eats', methods=['POST'])
def ue():
    addr = r.form['address']
    food = r.form['food']

    d = {}
    rests_lst = ue_scrape(addr, food, 10)
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        d[f"rest_{i}"] = rest.d_json

    return jsonify(d)


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(host="0.0.0.0")