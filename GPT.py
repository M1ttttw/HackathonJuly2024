from FoodClasses import Restaurant, FoodItem
from pydantic import BaseModel
from openai import OpenAI
import json


def get_cal_list(input_str: str, client) -> list:
    """ Using the given client and input string, return the calories list.

    :param input_str:
    :param client:
    :return:
    """
    # Use the input string as is. Use the beta version of gpt
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system",
             "content": "Given a list of food items and their descriptions, give an estimate (do not use a range of values) of how many calories each food item has"},
            {"role": "user", "content": input_str},
        ],
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "calories_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "calories_tuples": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {
                                        "type": "integer"
                                    },
                                    "item_calories": {
                                        "type": "integer"
                                    }
                                },
                                "required": ["item_id", "item_calories"],
                                "additionalProperties": False
                            },
                            "description": "A list of tuples containing an item id, and it's corresponding calories. Should be the same length as the number of items given!"
                        }
                    },
                    "required": ["calories_tuples"],
                    "additionalProperties": False
                }
            }
        }
    )

    cal_tuples = json.loads(completion.choices[0].message.content)['calories_tuples']
    cal_lst = [0] * len(cal_tuples)
    for i in range(len(cal_tuples)):
        cal_lst[i] = cal_tuples[i]['item_calories']

    return cal_lst


def acquire_calories(rest: Restaurant, items_per_it: int, char_lim = 4096) -> None:
    """ Calculate the calories for all the food items of the restaurant.

    :param rest:
    :param items_per_it:
    :return:
    """
    # Start a new client and pass on our input_str
    client = OpenAI(
        api_key="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")

    # Build an input string to pass on as input for ChatGPT. and build a results list of calories
    input_str = ""
    bld_lst = []
    i = 0
    for d_key in rest.catalogue:
        food_item = rest.catalogue[d_key]
        new_str = f"Item {i}. {food_item.name}\nItem {i} description: {food_item.desc}\n\n"
        tst_string = input_str + new_str

        # Test if we are over limit...
        if i >= items_per_it or len(tst_string) > char_lim:
            if i >= items_per_it:
                print(f"{i}th iteration, item overlimit...")
            else:
                print(f"{i}th iteration, character overlimit")

            # Use the input string as is and add on to the lst.
            bld_lst += get_cal_list(input_str, client)

            # Reset input string to include this item
            i = 0
            input_str = f"Item {i}. {food_item.name}\nItem {i} description: {food_item.desc}\n\n"
        else:
            input_str = tst_string

        i += 1

    # If there is still a non-empty input_str, that means there are some items left to pass on to gpt
    if input_str != "":
        bld_lst += get_cal_list(input_str, client)

    print(f"cal_list length: {len(bld_lst)}, catalogue length: {len(rest.catalogue)}")
    i = 0
    for d_key in rest.catalogue:
        # Iterate through the food items
        food_item = rest.catalogue[d_key]

        # Set the calories we got back from gpt and calculate the cpd for each item
        try:
            food_item.set_cal(bld_lst[i])
        except:
            food_item.set_cal(0)
        food_item.calc_cal_per_dollar()
        i += 1
