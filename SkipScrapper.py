from browser import sd_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from FoodClasses import Restaurant
import time

test_addr = "4820 201 st"
test_food = "Beef"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
web = webdriver.Chrome(options=options)

def sd_home_scrape():
    sd_init("4820 201 st", web)

    