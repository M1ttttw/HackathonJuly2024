from browser import dd_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from FoodClasses import Restaurant
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
web = webdriver.Chrome(options=options)

def dd_home_scrape():
    dd_init("4820 201 st","beef",web)
    SCROLL_PAUSE_TIME = 5
    last_height = web.execute_script("return document.body.scrollHeight")
    while True:
        web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = web.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    section = web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[1]/div/div[1]/div[1]/div/div/div[1]/div[1]/div[3]/div/div[1]/div/div[3]/div[1]/div")
    sections = section.find_elements(By.XPATH,"*")
    print(len(sections))
    rec_restaurants = sections[2]
    restaurants_lst = rec_restaurants.find_elements(By.XPATH,"*")
    try:
        restaurants = sections[0]
        restaurants_lst = restaurants_lst+ restaurants.find_elements(By.XPATH,"*")
    except:
        print("no rec restaurants")
    restaurant_desc = []
    cnt = 0
    for restaurant in restaurants_lst:
        cnt += 1
        print(cnt)
        try:
            desc = restaurant.text.split("\n")
            if desc[3] == "Closed":
                restaurant_desc = Restaurant(desc[0],)
            else:
                print(desc)
        except:
            print("fail")
    print(restaurant_name[0])
    print(len(restaurants_lst))
dd_home_scrape()
