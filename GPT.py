from FoodClasses import Restaurant, FoodItem
from pydantic import BaseModel
from openai import OpenAI


class CalList(BaseModel):
    calories: list[float]


# What is this?
# def dd_complete(adr,food,*args):
#     rest_lst = dd_scrape(adr,food,args[0],args[1])
#     for rest in rest_lst:
#         for item in rest_lst:
#             pass

def acquire_calories(rest: Restaurant) -> None:
    """ Calculate the calories for all the food items of the restaurant.

    :param rest:
    :return:
    """
    # Build a input string to pass on as input for ChatGPT
    input_str = ""
    for d_key in rest.catalogue:
        food_item = rest.catalogue[d_key]
        input_str += f"{food_item.name}\n{food_item.desc}\n\n"

    # Start a new client and pass on our input_str
    client = OpenAI(
        api_key="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")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Given a list of food items and their descriptions, give an estimate (do not use a range of values) of how many calories each food item has"},
            {"role": "user", "content": input_str},
        ],
        response_format=CalList
    )

    # Set the calories for each food_item, and calculate their cpd
    cal_list = completion.choices[0].message.parsed.calories
    i = 0
    for d_key in rest.catalogue:
        food_item = rest.catalogue[d_key]
        food_item.set_cal(cal_list[i])
        food_item.calc_cal_per_dollar()
        i += 1
