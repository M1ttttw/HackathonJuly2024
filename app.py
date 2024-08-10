from flask import Flask, render_template, jsonify
from flask import request as r

from SkipScrapper import sd_home_scrape
from DDscraper import dd_scrape
from UEscraper import ue_scrape


app = Flask(__name__)

@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/scrape', methods=['POST'])
def scrape():
    # Grab the data sent along with the request
    addr = r.form['address']
    food = r.form['food']
    scrape_t = int(r.form['scrape_type'])

    # Create a response json
    d = {"rests":[]}

    # Use the corresponding scraper
    if scrape_t == 0:
        rests_lst = sd_home_scrape(addr, food, 2)
    elif scrape_t == 1:
        rests_lst = dd_scrape(addr, food, 10)
    else:
        rests_lst = ue_scrape(addr, food, 10)

    # If the scraper doesn't have anything, just return a empty response
    if rests_lst is []:
        return jsonify({})
    for i, rest in enumerate(rests_lst):
        # Add the restaurant's d_json representation.
        rest.showcase_restaurant()
        d["rests"].append(rest.d_json)
    print(d)
    # We now have a dictionary representation ready to jsonify.
    return jsonify(d)


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(host="0.0.0.0")