from DDscraper import dd_scrape
from SkipScrapper import sd_home_scrape
from UEscraper import ue_scrape
from FoodClasses import Restaurant,FoodItem

def dd_complete(adr,food,*args):
    rest_lst = dd_scrape(adr,food,args[0],args[1])
    for rest in rest_lst:
        for item in rest_lst:
