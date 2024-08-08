from DDscraper import dd_scrape
from SkipScrapper import sd_home_scrape
from UEscraper import ue_scrape
from FoodClasses import Restaurant,FoodItem


# What is this?
def dd_complete(adr,food,*args):
    rest_lst = dd_scrape(adr,food,args[0],args[1])
    for rest in rest_lst:
        for item in rest_lst:
            pass

def acquire_calories(rest: Restaurant) -> None:
    """ Calculate the calories for all the food of the restaurant.

    :param rest:
    :return:
    """

    for d_key in rest.catalogue:
        food_item = rest.catalogue[d_key]

