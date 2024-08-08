from FoodClasses import Restaurant, FoodItem
from pydantic import BaseModel
from openai import OpenAI


class CalList(BaseModel):
    calories: list[float]


def get_cal_list(input_str: str, client) -> list:
    """ Using the given client and input string, return the calories list.

    :param input_str:
    :param client:
    :return:
    """
    # Use the input string as is
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system",
             "content": "Given a list of food items and their descriptions, give an estimate (do not use a range of values) of how many calories each food item has"},
            {"role": "user", "content": input_str},
        ],
        response_format=CalList
    )

    return completion.choices[0].message.parsed.calories


def acquire_calories(rest: Restaurant) -> None:
    """ Calculate the calories for all the food items of the restaurant.

    :param rest:
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
        new_str = f"{i}. {food_item.name}\n{food_item.desc}\n\n"
        tst_string = input_str + new_str

        # Test if we are over limit...
        if len(tst_string) > 4096:
            # Use the input string as is and add on to the lst.
            bld_lst += get_cal_list(input_str, client)

            # Reset input string to include this item
            input_str = ""
            input_str += new_str
        else:
            input_str = tst_string

        i += 1

    if input_str != "":
        bld_lst += get_cal_list(input_str, client)

    print(f"cal_list length: {len(bld_lst)}, catalogue length: {len(rest.catalogue)}")
    i = 0
    for d_key in rest.catalogue:
        food_item = rest.catalogue[d_key]
        food_item.set_cal(bld_lst[i])
        food_item.calc_cal_per_dollar()
        i += 1
