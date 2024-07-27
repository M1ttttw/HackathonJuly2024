

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
        if self.price == 0:
            self.cpd = self.calories / self.epsilon
        else:
            self.cpd = self.calories / self.price
        return self.cpd


