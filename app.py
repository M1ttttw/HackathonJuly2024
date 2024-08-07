from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/skip', methods=['POST'])
def sd_scrape():
    addr = request.form['address']
    food = request.form['food']

    print(f"received {addr} and {food}")
    return jsonify({})

@app.route('/dash', methods=['POST'])
def dd_scrape():
    addr = request.form['address']
    food = request.form['food']

    return jsonify({})

@app.route('/eats', methods=['POST'])
def ue_scrape():
    addr = request.form['address']
    food = request.form['food']

    return jsonify({})


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(debug=True)