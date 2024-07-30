from __future__ import annotations
from typing import Any, Optional
from browser import sd_init
from browser import wait_and_grab, wait_for_elem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from FoodClasses import Restaurant
import time

test_addr = "4820 201 st"
test_food = "Beef"
test_limit = 10

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
web = webdriver.Chrome(options=options)

def sd_home_scrape():
    # Navigate web driver to home page
    sd_init("4820 201 st", web)

    # Input the food into the search bar
    search_field = web.find_element(By.XPATH, '//*[@id="header-search"]')
    search_field.send_keys(test_food)

    # Wait and grab the food in items button
    items_button = wait_and_grab(web, By.XPATH, '//*[@id="root"]/div/div[1]/div/header/div/div/div[2]/div[3]/div[2]/div/button')
    items_button.click()

    # Next, we want to wait and find the restaurant list
    wait_for_elem(web, By.XPATH, '//*[@id="root"]/div/main/div/div/div/div/ul/li[1]/div/div[1]/div/a')
    rests_parent = wait_and_grab(web, By.XPATH, "/html/body/div[2]/div/main/div/div/div/div/ul")
    rests_UI_list = rests_parent.find_elements(By.XPATH, "*")
    print(f"there are {len(rests_UI_list)} restaurants currently in view")

    # Iterate through a fixed amount of restaurants
    for rest_UI in rests_UI_list:
        # Grab the url of the restaurant we want to check out
        rest_url = wait_and_grab(rest_UI, By.XPATH, ".//div/div[1]/a")
        rest_url_w_food = rest_url.get_attribute("href") + f"?search={test_food}"
        print(rest_url_w_food)

        # Start a new driver set to our new rest_url_w_food
        rest_driver = webdriver.Chrome(options=options)
        rest_driver.get(rest_url_w_food)

        # Find the container containing the subdivisions of a menu
        mega_container = wait_and_grab(rest_driver, By.XPATH, '//*[@id="ComponentsContainer"]/div[2]')
        item_section_lst = mega_container.find_elements(By.XPATH, "*")
        for section in item_section_lst:
            # Then Find the item list of that respective subdivision of the menu
            # item_list_parent = section.find_element(By.XPATH, "styles__ItemsList-sc-120s71t-2 hdduBA")
            item_list_parent = wait_and_grab(section, By.XPATH, ".//div/div/ul")
            item_list = item_list_parent.find_elements(By.XPATH, "*")

            # We then iterate through the items in that subdivision.
            for item in item_list:
                # Then grab everything you need about the food item
                
                print(item.text)

        # Once we are done with the restaurant, close the menu
        rest_driver.close()

sd_home_scrape()