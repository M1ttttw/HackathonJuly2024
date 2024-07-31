from __future__ import annotations
from typing import Any, Optional
from browser import sd_init
from browser import wait_and_grab, wait_for_elem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from FoodClasses import Restaurant, FoodItem
import time

test_addr = "4820 201 st"
test_food = "Beef"
test_limit = 10

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
web = webdriver.Chrome(options=options)

def sd_home_scrape(addr, food, limit):
    # Navigate web driver to home page
    sd_init(addr, web)

    # Input the food into the search bar
    search_field = web.find_element(By.XPATH, '//*[@id="header-search"]')
    search_field.send_keys(food)

    # Wait and grab the food in items button
    items_button = wait_and_grab(web, By.XPATH, '//*[@id="root"]/div/div[1]/div/header/div/div/div[2]/div[3]/div[2]/div/button')
    items_button.click()

    # Next, we want to wait and find the restaurant list
    wait_for_elem(web, By.XPATH, '//*[@id="root"]/div/main/div/div/div/div/ul/li[1]/div/div[1]/div/a')
    rests_parent = wait_and_grab(web, By.XPATH, "/html/body/div[2]/div/main/div/div/div/div/ul")
    rests_UI_list = rests_parent.find_elements(By.XPATH, "*")
    print(f"there are {len(rests_UI_list)} restaurants currently in view")

    # Keep a counter to go through a limited number of restaurant.
    rest_count = 0

    # Iterate through a fixed amount of restaurants
    for rest_UI in rests_UI_list:
        # Break away from the loop once we've looked through a fixed number of restaurants
        if rest_count >= limit:
            break

        # Grab the url of the restaurant we want to check out
        rest_url = wait_and_grab(rest_UI, By.XPATH, ".//div/div[1]/a").get_attribute("href")
        print(rest_url)

        # Start a new driver set to our new rest_url_w_food
        rest_driver = webdriver.Chrome(options=options)
        rest_driver.get(rest_url)

        # Convenience store pages are very different, take advantage of this!
        try:
            # Find the container containing the subdivisions of a menu
            mega_container = wait_and_grab(rest_driver, By.XPATH, '//*[@id="ComponentsContainer"]/div')
        except:
            print("Convenience Store Detected")
            continue

        # We need to know the restaurant's information, thus, we grab the restaurant's info
        rest_info = rest_UI.text.split("\n")
        rest_name, rest_deliv_time_str, rest_deliv_fee_str, rest_rate = (rest_info[0], rest_info[1], rest_info[2],
                                                                         float(rest_info[3]))

        # Cut out the fat in rest_deliv_time_str
        rest_deliv_time_split = rest_deliv_time_str.split(" ")
        rest_deliv_time = int(rest_deliv_time_split[2]) - int(rest_deliv_time_split[0])

        # Cut out the fat in rest_deliv_fee_str
        rest_deliv_fee_split = rest_deliv_fee_str.split(" ")
        rest_deliv_fee = float(rest_deliv_fee_split[0][1:])







        item_section_lst = mega_container.find_elements(By.XPATH, "*")
        for section in item_section_lst:
            # There are some sections that could be talking about allergies or place settings, so we skip over those
            section_name = section.text.split("\n")[0]
            if section_name == "Allergies & Intolerances" or section_name == "Place Settings":
                continue

            # Then Find the item list of that respective subdivision of the menu
            item_list_parent = wait_and_grab(section, By.XPATH, ".//div/div/ul")
            item_list = item_list_parent.find_elements(By.XPATH, "*")

            # # We then iterate through the items in that subdivision.
            for item in item_list:
                # Skip over any items that have no children
                item_children = item.find_elements(By.XPATH, "*")
                if len(item_children) == 0:
                    print("Fake Item detected")
                    continue

                # Then grab everything you need about the food item
                print(item.text.split("\n"))

        # Once we are done with the restaurant, close the webdriver
        rest_driver.close()
        rest_count += 1

    print(f"Successfully Went through {rest_count} stores")


# This is a test
sd_home_scrape(test_addr, test_food, test_limit)