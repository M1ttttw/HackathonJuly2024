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
    isSD = r.form['skip']
    isDD = r.form['dash']
    isUE = r.form['eats']

    # Create a response json
    d = {"rests":[]}

    # Use the corresponding scraper
    rests_lst = []
    if isSD == 'true':
        rests_lst += sd_home_scrape(addr, food, 6)
    if isDD == 'true':
        rests_lst += dd_scrape(addr, food, 6)
    if isUE == 'true':
        hacky_fix = 0
        while hacky_fix<5:
            try:
                rests_lst += ue_scrape(addr, food, 6)
                hacky_fix = 5
            except:
                print("ue_broken")
                hacky_fix += 1

    # If the scraper doesn't have anything, just return a empty response
    if rests_lst is []:
        return jsonify({})
    for rest in rests_lst:
        # Add the restaurant's d_json representation.
        rest.showcase_restaurant()
        d["rests"].append(rest.d_json)

    # Sort by restaurant cpd.
    d["rests"].sort(key=lambda x: x["rest_cpd"], reverse=True)

    print(d)
    # We now have a dictionary representation ready to jsonify.
    return jsonify(d)


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(port=3000)