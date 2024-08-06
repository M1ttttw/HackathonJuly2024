from __future__ import annotations
from typing import Any, Optional

#extracts the first int in a string
def clean_int(num_str):
    num = ""
    has_num = False
    for i in num_str:
        if i.isnumeric():
            num += i
            has_num = True
        elif not i.isnumeric() and has_num:
            break

    return int(num)
#extracts the first float in a string
def clean_float(num_str):
    num = ""
    has_dot = False
    first_num = False
    for i in num_str:
        if i.isnumeric():
            num += i
            first_num = True
        elif i == "." and not has_dot:
            has_dot = True
            num += i
        elif first_num:
            break

    return float(num)
class FoodItem:
    """ A class that represents a food item.

    name: the string that contains the item's name
    desc: a string that contains the item's description
    price: a float that contains how expensive the item is.
    calories: a float that contains how many calories the item is
    cpd: a float that represents calories per dollar
    image: a string representing the image
    d_json: a dictionary representation of this item, for json purposes
    """
    name: str
    desc: str
    price: float
    calories: float
    cpd: float
    image: str
    d_json: dict

    def __init__(self, food_name: str, food_desc: str, food_price: float,image:str) -> None:
        self.name = food_name
        self.desc = food_desc
        self.price = food_price
        self.image = image
        self.calories = 0
        self.cpd = 0

        # Build a dictionary representing this item
        self.d_json = {}
        self.d_json["name"] = food_name
        self.d_json['desc'] = food_desc
        self.d_json["price"] = food_price
        self.d_json["image"] = image
        self.d_json["calories"] = 0
        self.d_json["cpd"] = 0

    def calc_cal_per_dollar(self, epsilon=0.01) -> float:
        """ Calculate, set and return the calories per dollar (cpd)
        :return:
        """
        # If the food is free, then division by a smaller number bloats the CPD as needed.
        self.cpd = self.calories / (self.price + epsilon)
        self.d_json["cpd"] = self.cpd

        return self.cpd
    def __str__(self):
        return "\nname:"+self.name+"\ndescription:" + self.desc + "\nprice:"+str(self.price)+"\nimage link:"+self.image


class Restaurant:
    """ A class that represents contains information about a restaurant

    name: a string that represents the restaurant's name
    addr: a string that distinguishes which specific restaurant
    app: a string that represents which app the restaurant was found.
    url: a string that represents the url of the restaurant
    catalogue: a list of FoodItems
    rest_cpd: the calories per dollar score of all the items in the catalogue here.
    rating: the rating of the restaurant
    dist_to_user: How far the restaurant is from the user. Leave -1 as an error or placeholder value
    deliv_fee: this is how much the delivery fee of the restaurant is
    discounts: this is the list of discounts that are applicable to that restaurant
    review_count: the number of reviews for the restaurant. Leave -1 as an error or placeholder value
    deliv_time: the approximate time it takes to deliver food to the user's location
    d_json: a dictionary representing this restaurant for json purposes.
    """
    name: str
    addr: str
    app: str
    url: str
    catalogue: dict
    rest_cpd: float
    rating: float
    dist_to_user: float
    deliv_fee: float
    discounts: list[Any] # I'll leave this as any while we figure out how discounts are represented.
    review_count: int
    deliv_time: float
    d_json: dict

    def __init__(self, rest_name: str, rest_address: str, rest_app: str, rest_rating: float, rest_dist: float,
                 rest_fee: float, rev_count: int, rest_deliv_time: float, rest_url: str) -> None:
        self.name = rest_name
        self.addr = rest_address
        self.app = rest_app
        self.url = rest_url
        self.catalogue = dict()
        self.rating = rest_rating
        self.dist_to_user = rest_dist
        self.deliv_fee = rest_fee
        self.discounts = []
        self.review_count = rev_count
        self.deliv_time = rest_deliv_time
        self.rest_cpd = 0

        # Build a dictionary representing this item
        self.d_json = {}
        self.d_json["name"] = rest_name
        self.d_json["addr"] = rest_address
        self.d_json["app"] = rest_app
        self.d_json["url"] = rest_url
        self.d_json["catalogue"] = {}
        self.d_json["rating"] = rest_rating
        self.d_json["dist_to_user"] = rest_dist
        self.d_json["deliv_fee"] = rest_fee
        self.d_json["discounts"] = {}
        self.d_json["discounts"][1] = []
        self.d_json["discounts"][2] = []
        self.d_json["discounts"][3] = []
        self.d_json["review_count"] = rev_count
        self.d_json["deliv_time"] = rest_deliv_time
        self.d_json["rest_cpd"] = 0

    def add_addr(self,address:str):
        self.addr = address
        self.d_json["addr"] = address

    def add_item(self, food_item: FoodItem) -> None:
        """ Add the <food_item> to the catalogue

        # Preconditions: the food_item must already be configured and have a cpd.

        :param food_item:
        :return:
        """
        self.catalogue[food_item.name] = food_item
        self.d_json["catalogue"][food_item.name] = food_item.d_json

    def add_discount(self,discount_str:str,food = None,food_name = ""):
        if self.app == "DD":
            disc_dsc = discount_str.split(" ")
            dsc_type = 0
            if "Spend" in discount_str:
                dsc_type = 1
                spend = disc_dsc[1]
                spend_int = clean_int(spend)
                save = disc_dsc[3]
                save_int = clean_int(save)
                self.discounts.append((dsc_type,[spend_int,save_int]))
                self.d_json["discounts"][dsc_type].append([spend_int, save_int])
            elif "up" in discount_str:
                dsc_type = 2
                dsc = disc_dsc[0]
                dsc_int = clean_int(dsc)
                upto = disc_dsc[4]
                upto_int = clean_int(upto)
                self.discounts.append((dsc_type, [dsc_int, upto_int]))
                self.d_json["discounts"][dsc_type].append([dsc_int, upto_int])
            elif "delivery" in discount_str:
                dsc_type = 3
                self.discounts.append((dsc_type, []))

                # Why dsc_type, []? what's the empty list for?
                self.d_json["discounts"][dsc_type].append([])
        elif self.app == "UE":
            if "Buy" in discount_str:
                dsc_type = 1
                self.discounts.append((dsc_type,food,food_name))

                # What is the food param? like a FoodItem class? not sure that can be turned into a json, so let's just
                # use it's food item name, since we already have it's dictionary representation, we just have to find it
                self.d_json["discounts"][dsc_type].append(food_name)
            elif "purchase" in discount_str:
                dsc_type = 2
                amount = clean_int(discount_str)
                self.discounts.append((dsc_type,(amount,food,food_name)))
                self.d_json["discounts"][dsc_type].append([food_name, amount])
        elif self.app == "SkipTheDishes":
            if "Free" in discount_str:
                dsc_type = 1
                discnt_desc = discount_str.split(" ")
                price = clean_int(discnt_desc[-1])
                item_name = ""
                for w in discnt_desc[1:-3]:
                    item_name += w
                    item_name += " "
                item_name = item_name[:-1]
                self.discounts.append((1,(self.catalogue[item_name],price)))
                self.d_json["discounts"][dsc_type].append([self.catalogue[item_name], price])
            elif "off" in discount_str:
                dsc_type = 2
                discnt_desc = discount_str.split(" ")
                res1 = clean_int(discnt_desc[0])
                res2 = clean_int(discnt_desc[-1])

                self.discounts.append((2,(res1, res2)))
                self.d_json["discounts"][dsc_type].append([res1, res2])

    def __str__(self):
        string = ("name:"+self.name + "\naddress:"+ self.addr+"\napp:"+self.app+
                "\ndelivery fee:"+str(self.deliv_fee)+"\ndelivery time:"+str(self.deliv_time)+"\ndistance to user:"+str(self.dist_to_user)
                +"\nrating:"+str(self.rating)+"\naverage calories per dollar:"+str(self.rest_cpd)+"\nreview count:"+str(self.review_count)
                +"\ndiscounts:"+str(self.discounts))+"\nmenu items:"
        for i in self.catalogue:
            string += i + str(self.catalogue[i]) + "\n"
        return string

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

        # TODO: Sense catalogue is now a dictionary, this method needs to be rewritten...
        # sort by cpd
        self.catalogue.sort(key=lambda x: x.cpd, reverse=True)
        final_list = self.catalogue[0: num]

        # Calculate and set the CPD of the restaurant
        acc = 0
        for item in final_list:
            acc += item.cpd

        self.rest_cpd = acc
        return final_list

