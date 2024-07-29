from __future__ import annotations
from typing import Any, Optional


class FoodItem:
    """ A class that represents a food item.

    name: the string that contains the item's name
    desc: a string that contains the item's description
    price: a float that contains how expensive the item is.
    calories: a float that contains how many calories the item is
    """
    name: str
    desc: str
    price: float
    calories: float
    cpd: float

    def __init__(self, food_name: str, food_desc: str, food_price: float) -> None:
        self.name = food_name
        self.desc = food_desc
        self.price = food_price

    def calc_cal_per_dollar(self, epsilon=0.01) -> float:
        """ Calculate, set and return the calories per dollar (cpd)
        :return:
        """
        # If the food is free, then division by a smaller number bloats the CPD as needed.
        self.cpd = self.calories / (self.price + epsilon)
        return self.cpd


class Restaurant:
    """ A class that represents contains information about a restaurant

    name: a string that represents the restaurant's name
    addr: a string that distinguishes which specific restaurant
    app: a string that represents which app the restaurant was found.
    catalogue: a list of FoodItems
    rest_cpd: the calories per dollar score of all the items in the catalogue here.

    """
    name: str
    addr: str
    app: str
    catalogue: list[FoodItem]
    rest_cpd: float

    def __init__(self, rest_name: str, rest_dist: float,rest_delivery_fee:float, rest_app: str) -> None:
        self.name = rest_name
        self.addr = rest_address
        self.app = rest_app
        self.catalogue = []

    def add_item(self, food_item: FoodItem) -> None:
        """ Add the <food_item> to the catalogue

        # Preconditions: the food_item must already be configured and have a cpd.

        :param food_item:
        :return:
        """
        self.catalogue.append(food_item)

    def showcase_restaurant(self, show_num=5) -> list[FoodItem]:
        """ Sort the catalogue by cpd, and return the first <show_num> items. Calculate and set the cpd score for the
        restaurant

        :param show_num:
        :return:
        """
        # Clamp the parameter between 0 and the length of the catalogue
        if show_num < 0:
            num = 0
        elif show_num > len(self.catalogue):
            num = len(self.catalogue)
        else:
            num = show_num

        # sort by cpd
        self.catalogue.sort(key=lambda x: x.cpd, reverse=True)
        final_list = self.catalogue[0: num]

        # Calculate and set the CPD of the restaurant
        acc = 0
        for item in final_list:
            acc += item.cpd

        self.rest_cpd = acc
        return final_list




