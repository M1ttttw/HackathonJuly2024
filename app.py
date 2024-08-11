from flask import Flask, render_template, jsonify
from flask import request as r
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from selenium import webdriver

from SkipScrapper import sd_rest_scrape,sd_menu_scrape
from DDscraper import dd_rest_scrape,dd_menu_scrape
from UEscraper import ue_rest_scrape,ue_menu_scrape


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
engine = create_engine('sqlite:///db.sqlite3')
Session = sessionmaker(engine)
db = SQLAlchemy(app)
class Base(DeclarativeBase):
    pass
class Restaurants(Base):
    __tablename__ = "restaurants"
    name = db.Column(db.String(100), nullable=False)
    addr = db.Column(db.String(100))
    url = db.Column(db.String(200), primary_key=True)
    app = db.Column(db.String(20),nullable = False)
    rating = db.Column(db.Integer)
    review_cnt = db.Column(db.Integer)

    def __repr__(self):
        return f'<restaurants {self.name}>'
class FoodItem(Base):
    __tablename__ = "food_item"
    name = db.Column(db.String(100),primary_key=True)
    desc = db.Column(db.Text)
    rest_url = db.Column(db.String(200),ForeignKey(Restaurants.url), primary_key=True)
    price = db.Column(db.Float,nullable = False)
    image = db.Column(db.Text)
    calories = db.Column(db.Integer)

    def __repr__(self):
        return f'<FoodItems {self.name}>'
@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/scrape', methods=['POST'])
def scrape():
    with Session() as session:
        # Base.metadata.drop_all(engine)
        # Base.metadata.create_all(engine)
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
        uqe_urls = []

        if isSD == 'true':
            result = sd_rest_scrape(addr,food,2)
            urls = result[1]
            vr = result[0]
            web = result[2]
            for url in urls:
                print(url)
                statement = select(Restaurants).filter_by(url=url)
                if len(session.execute(statement).all())==0:
                    uqe_urls.append(url)
            r_lst = sd_menu_scrape(addr, food, vr)
            for res in r_lst:
                rest = Restaurants(name=res.name, addr=res.addr, app=res.app, url=res.url, rating=res.rating,
                                   review_cnt=res.review_count)
                session.add(rest)
            web.close()
            rests_lst += r_lst
        if isDD == 'true':
            result = dd_rest_scrape(addr, food, 2)
            urls = result[0]
            vr = result[1]
            web = result[2]
            for url in urls:
                print(url)
                statement = select(Restaurants).filter_by(url=url)
                if len(session.execute(statement).all())==0:
                    uqe_urls.append(url)
            r_lst = dd_menu_scrape(addr, food, vr,urls)
            for res in r_lst:
                rest = Restaurants(name=res.name, addr=res.addr, app=res.app, url=res.url, rating=res.rating,
                                   review_cnt=res.review_count)
                session.add(rest)
            web.close()
        if isUE == 'true':
            result = ue_rest_scrape(addr, food)
            urls = result[0]
            vr = result[1]
            web = result[2]
            for url in urls:
                print(url)
                statement = select(Restaurants).filter_by(url=url)
                if len(session.execute(statement).all())==0:
                    uqe_urls.append(url)
            r_lst = ue_menu_scrape(addr, food, vr,urls)
            for res in r_lst:
                rest = Restaurants(name=res.name, addr=res.addr, app=res.app, url=res.url, rating=res.rating,
                                   review_cnt=res.review_count)
                session.add(rest)
            web.close()

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
        session.commit()
    # We now have a dictionary representation ready to jsonify.
    return jsonify(d)


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(port=3000)