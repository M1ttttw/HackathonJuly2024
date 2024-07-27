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

    epsilon = 0.01

    def __init__(self, food_name: str, food_desc: str, food_price: float) -> None:
        self.name = food_name
        self.desc = food_desc
        self.price = food_price

    def calc_cal_per_dollar(self) -> float:
        """ Calculate, set and return the calories per dollar (cpd)
        :return:
        """
        # If the food is free, then division by a smaller number bloats the CPD as needed.
        self.cpd = self.calories / (self.price + self.epsilon)
        return self.cpd


