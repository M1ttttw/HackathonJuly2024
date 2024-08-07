from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def init():
    return render_template("DealDash.html")

if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(debug=True)