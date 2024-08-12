from flask import Flask, render_template, jsonify
from flask import request as r
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from FoodClasses import FoodItem as FI
from FoodClasses import Restaurant
from selenium import webdriver

from SkipScrapper import sd_rest_scrape,sd_menu_scrape
from DDscraper import dd_rest_scrape,dd_menu_scrape
from UEscraper import ue_rest_scrape,ue_menu_scrape


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
engine = create_engine('sqlite:///db.sqlite3',connect_args={'timeout': 30})
Session = sessionmaker(engine)
db = SQLAlchemy(app)
class Base(DeclarativeBase):
    pass
class Restaurants(Base):
    __tablename__ = "restaurants"
    name = db.Column(db.String(100), nullable=False)
    addr = db.Column(db.String(100))
    url = db.Column(db.String(200), primary_key=True)
    rest_img = db.Column(db.String(200))
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
    def db_retrieve(addr,food,rest_scraper,menu_scraper):
        rests_lst = []
        result = rest_scraper(addr, food)
        urls = result[1]
        vr = result[0]
        web = result[2]
        urls = urls[0:limit]
        vr = vr[0:limit]
        uqe_urls = {}
        n_uqe_urls = {}
        url_cnt = 0
        for url in urls:
            print(url)
            statement = select(Restaurants).filter_by(url=url)
            if len(session.execute(statement).all()) == 0:
                uqe_urls[url] = vr[url_cnt]
            else:
                n_uqe_urls[url] = vr[url_cnt]
            url_cnt += 1
        vr = []
        for i in uqe_urls:
            vr.append(uqe_urls[i])
        if len(list(uqe_urls.keys())) > 0:
            r_lst = menu_scraper(addr, food, vr, list(uqe_urls.keys()))
            for res in r_lst:
                rest = Restaurants(name=res.name, addr=res.addr, app=res.app, url=res.url, rating=res.rating,
                                   review_cnt=res.review_count,rest_img = res.image)
                session.add(rest)
                for food in res.catalogue:
                    fi = res.catalogue[food]
                    food_item = FoodItem(name=fi.name, desc=fi.desc, rest_url=res.url, price=fi.price, image=fi.image,
                                         calories=fi.calories)
                    session.add(food_item)
            rests_lst += r_lst
        if len(list(n_uqe_urls.keys())) > 0:
            r_lst = []
            for url in list(n_uqe_urls.keys()):
                statement = select(Restaurants).filter_by(url=url)
                rest = session.execute(statement).first()[0]
                real_rest = Restaurant(rest.name, rest.addr, rest.app, rest.rating, 0, 0, rest.review_cnt, 0, rest.url,rest.rest_img)
                r_lst.append(real_rest)
                statement = select(FoodItem).filter_by(rest_url=url)
                r_food = session.execute(statement).all()
                for f in r_food:
                    f = f[0]
                    fi = FI(f.name, f.desc, f.price, f.image)
                    fi.set_cal(f.calories)
                    real_rest.add_item(fi)
            rests_lst += r_lst
        web.close()
        session.commit()
        return rests_lst
    with Session() as session:
        # Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
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

        limit = 2
        if isSD == 'true':
            rests_lst += db_retrieve(addr,food,sd_rest_scrape,sd_menu_scrape)

        if isDD == 'true':
            rests_lst += db_retrieve(addr,food,dd_rest_scrape,dd_menu_scrape)
        if isUE == 'true':
            rests_lst += db_retrieve(addr,food,ue_rest_scrape,ue_menu_scrape)

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