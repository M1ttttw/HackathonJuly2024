from flask import Flask, render_template, jsonify
from flask import request as r
from threading import Lock

from SkipScrapper import sd_home_scrape
from DDscraper import dd_scrape
from UEscraper import ue_scrape


app = Flask(__name__)
req_mutex = Lock()

@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/scrape', methods=['POST'])
def scrape():
    # Acquire the lock and prevent other request threads from running
    req_mutex.acquire()

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
        rests_lst += sd_home_scrape(addr, food, 2)
    if isDD == 'true':
        rests_lst += dd_scrape(addr, food, 6)
    if isUE == 'true':
        rests_lst += ue_scrape(addr, food, 6)

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

    # Release the lock
    req_mutex.release()

    # We now have a dictionary representation ready to jsonify.
    return jsonify(d)


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(port=3000)