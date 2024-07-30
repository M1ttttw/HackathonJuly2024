from __future__ import annotations
from typing import Any, Optional
from browser import sd_init
from browser import wait_and_grab
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
    rests_parent = wait_and_grab(web, By.XPATH, "/html/body/div[2]/div/main/div/div/div/div/ul")
    rests_UI_list = rests_parent.find_elements(By.XPATH, "*")

    # Iterate through a fixed amount of restaurants
    for rest_UI in rests_UI_list[0: test_limit]:
        # Create a new web driver to check the restaurant out
        # rest_web = webdriver.Chrome(options=options)
        print(rest_UI.text)

        pass

sd_home_scrape()