from flask import Flask, render_template, jsonify
from flask import request as r
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from FoodClasses import FoodItem as FI
from FoodClasses import Restaurant
from selenium import webdriver
from threading import Lock

from SkipScrapper import sd_rest_scrape,sd_menu_scrape
from DDscraper import dd_rest_scrape,dd_menu_scrape
from UEscraper import ue_rest_scrape,ue_menu_scrape


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
engine = create_engine('sqlite:///db.sqlite3',connect_args={'timeout': 30})
Session = sessionmaker(engine)
db = SQLAlchemy(app)
req_mutex = Lock()

class Base(DeclarativeBase):
    pass
#definint our db tables
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
class Discount(Base):
    __tablename__ = "discount"
    disc_type = db.Column(db.Integer)
    rest_url = db.Column(db.String(200),ForeignKey(Restaurants.url))
    arg_food = db.Column(db.String(200),ForeignKey(FoodItem.name))
    arg0 = db.Column(db.Integer)
    arg1 = db.Column(db.Integer)
    arg2 = db.Column(db.Integer)
    disc_id = db.Column(db.Integer)
    __table_args__ = (PrimaryKeyConstraint(rest_url, disc_id),{},)
class Banned(Base):
    __tablename__ ="banned_urls"
    url = db.Column(db.String(200),primary_key = True)
@app.route('/')
def init():
    return render_template("DealDash.html")

@app.route('/scrape', methods=['POST'])
def scrape():
    #function that calls our scrapers and returns the scraped infos
    def db_retrieve(addr,food,rest_scraper,menu_scraper,limit):
        rests_lst = []
        #rest scraper scrapes the avaliable restaurants nearby
        result = rest_scraper(addr, food)
        urls = result[1]
        vr = result[0]
        web = result[2]
        urls = urls[0:limit]
        vr = vr[0:limit]
        uqe_urls = {}
        n_uqe_urls = {}
        url_cnt = 0
        b_url_cleaned = []
        #go through each url and scrape if it is not in our database
        for url in urls:
            print(url)
            #removes unessesary php arguments
            cleaned_url = url.split("?")[0]
            statement = select(Restaurants).filter_by(url=cleaned_url)
            statement2 = select(Banned).filter_by(url=cleaned_url)
            #b_urls are banned stores that have a different layout (liquor stores/convinience stores)
            b_urls = session.execute(statement2).all()
            for u in b_urls:
                b_url_cleaned.append(u[0].url)
            r_query = session.execute(statement).all()
            b_query = session.execute(statement2).all()
            #if restaurant is not banned and not inside our db then it is unqiue and we must scrape it
            if len(r_query) == 0 and len(b_query)==0:
                uqe_urls[url] = vr[url_cnt]
            #else if it is not banned but inside out db then we pull it
            elif len(b_query)==0:
                n_uqe_urls[url] = vr[url_cnt]
            url_cnt += 1
        vr = []
        for i in uqe_urls:
            vr.append(uqe_urls[i])
        #for all unique restaurants (restaurants not inside our db) we scrape it and we store it in our db
        if len(list(uqe_urls.keys())) > 0:
            data = menu_scraper(addr, food, vr, list(uqe_urls.keys()))
            r_lst = data[0]
            for res in r_lst:
                dsc_cnt = 0
                cleaned_url = res.url.split("?")[0]
                rest = Restaurants(name=res.name, addr=res.addr, app=res.app, url=cleaned_url, rating=res.rating,
                                   review_cnt=res.review_count,rest_img=res.image)
                session.add(rest)
                for food in res.catalogue:
                    fi = res.catalogue[food]
                    food_item = FoodItem(name=fi.name, desc=fi.desc, rest_url=cleaned_url, price=fi.price, image=fi.image,
                                         calories=fi.calories)
                    session.add(food_item)
                for dsc in res.discounts:

                    f_name = None
                    args = [None,None,None]
                    dsc_type = dsc[0]
                    dsc_arg = dsc[1]
                    for i in range(len(dsc_arg)):
                        if type(dsc_arg[i]) == str:
                            f_name = dsc_arg[i]
                        else:
                            args[i]=dsc_arg[i]
                    discount = Discount(disc_type = dsc_type,rest_url = cleaned_url,arg_food = f_name,arg0=args[0],arg1=args[1],arg2=args[2],disc_id=dsc_cnt)
                    dsc_cnt += 1
                    session.add(discount)
            #if there are any timeouts then we add it to the banned urls
            b_lst = data[1]
            for b in b_lst:
                bq_statement = select(Banned).filter_by(url=b)
                b_query = session.execute(bq_statement).all()

                # Add this to the banned database only if it hasn't existed prior
                if len(b_query) == 0:
                    br = Banned(url=b)
                    session.add(br)

            rests_lst += r_lst
        #for all the none unique restaurants (resturants that exists in our db) we pull it
        if len(list(n_uqe_urls.keys())) > 0:
            r_lst = []
            for url in list(n_uqe_urls.keys()):
                cleaned_url = url.split("?")[0]
                statement = select(Restaurants).filter_by(url=cleaned_url)
                rest = session.execute(statement).first()[0]
                real_rest = Restaurant(rest.name, rest.addr, rest.app, rest.rating, 0, 0, rest.review_cnt, 0,cleaned_url,rest.rest_img)
                r_lst.append(real_rest)
                statement = select(FoodItem).filter_by(rest_url=cleaned_url)
                r_food = session.execute(statement).all()
                for f in r_food:
                    f = f[0]
                    fi = FI(f.name, f.desc, f.price, f.image)
                    fi.set_cal(f.calories)
                    fi.calc_cal_per_dollar()
                    real_rest.add_item(fi)
                statement = select(Discount).filter_by(rest_url=cleaned_url)
                r_discount = session.execute(statement).all()
                discounts = []
                for disc in r_discount:
                    args = []
                    d = disc[0]
                    if d.arg_food is not None:
                        args.append(d.arg_food)
                    if d.arg0 is not None:
                        args.append(d.arg0)
                        if d.arg1 is not None:
                            args.append(d.arg1)
                            if d.arg2 is not None:
                                args.append(d.arg2)
                    real_rest.d_json["discounts"][d.disc_type].append(args)
                    discounts.append((d.disc_type,args))
                real_rest.discounts = discounts
            rests_lst += r_lst
        web.close()
        session.commit()
        return rests_lst
    with Session() as session:
        try:
            # Acquire the lock
            req_mutex.acquire()

            # Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            # Grab the data sent along with the request
            addr = r.form['address']
            food = r.form['food']
            isSD = r.form['skip']
            isDD = r.form['dash']
            isUE = r.form['eats']
            loadCnt = int(r.form["loadCnt"])
            avg_load = loadCnt//3
            # Create a response json
            d = {"rests":[]}

            # Use the corresponding scraper
            rests_lst = []

            if isSD == 'true':
                try:
                    rests_lst += db_retrieve(addr,food,sd_rest_scrape,sd_menu_scrape,(loadCnt-avg_load*3)+avg_load)
                except:
                    pass
            if isDD == 'true':
                rests_lst += db_retrieve(addr,food,dd_rest_scrape,dd_menu_scrape,avg_load)
            if isUE == 'true':
                rests_lst += db_retrieve(addr,food,ue_rest_scrape,ue_menu_scrape,avg_load)

            # If the scraper doesn't have anything, just return a empty response
            if rests_lst is []:
                req_mutex.release()
                return jsonify({})
            for rest in rests_lst:
                # Add the restaurant's d_json representation.
                print(rest.name)
                print(len(rest.catalogue))
                print(rest.app)
                rest.showcase_restaurant(filter=food)
                d["rests"].append(rest.d_json)

            # Sort by restaurant cpd.
            d["rests"].sort(key=lambda x: x["rest_cpd"], reverse=True)

            print(d)
        except Exception as e:
            # Errors may cause deadlocks between requests! So release locks before errors happen
            req_mutex.release()
            raise e # This is cursed, but we should at least let the client know that something happened...

    # We are done, release the mutex.
    req_mutex.release()

    # We now have a dictionary representation ready to jsonify.
    return jsonify(d)


if __name__ == "__main__":
    # It's already preset to run this html doc on a local server
    app.run(port=3000)