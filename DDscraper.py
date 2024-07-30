from browser import dd_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from FoodClasses import Restaurant
from FoodClasses import FoodItem
from browser import wait_and_grab
from bs4 import BeautifulSoup
import time
import threading

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")
web = webdriver.Chrome(options=options)



class ScrapeThread(threading.Thread):
    def __init__(self, url,food,restaurant):
        threading.Thread.__init__(self)
        self.url = url
        self.food = food
        self.restaurant = restaurant

    def run(self):
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(1)
        # scrl_cnt = 0
        # SCROLL_PAUSE_TIME = 2
        # last_height = driver.execute_script("return document.body.scrollHeight")
        # while scrl_cnt < 5:
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     time.sleep(SCROLL_PAUSE_TIME)
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         break
        #     last_height = new_height
        #     scrl_cnt += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        item_fld = wait_and_grab(driver,By.ID,"item-search-field")
        item_fld.send_keys(self.food)
        # categories = driver.find_elements(By.CSS_SELECTOR,".sc-75da66f4-0.jvBEhF")
        # food_items = []
        # for category in categories:
        #     food_items = food_items + category.find_element(By.CSS_SELECTOR, ".sc-234bce1d-0.cbmNka").find_element(By.TAG_NAME, "div").find_elements(By.TAG_NAME, "div")
        # time.sleep(100)

        cnt = 0
        while cnt < 5:
            food_items = driver.find_elements(By.CSS_SELECTOR, ".sc-234bce1d-2.hAZmjs")
            for food_item in food_items:
                desc = food_item.text.split("\n")
                print(desc)
                image = ""
                try:
                    image = food_item.find_element(By.TAG_NAME,"source").get_attribute("srcset")
                    print("image found")
                except:
                    print("image not found")
                    image = "not found"
                if len(desc) == 4:
                    self.restaurant.add_item(FoodItem(desc[0],desc[1],float(desc[2][3:]),image))
                elif len(desc) == 3:
                    self.restaurant.add_item(FoodItem(desc[0], "", float(desc[1][3:]), image))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(len(food_items))
            cnt += 1
        driver.close()

        # do something with the page source

def dd_home_scrape(adr,food):
    dd_init(adr,food,web)
    # scrl_cnt = 0
    # SCROLL_PAUSE_TIME = 5
    # last_height = web.execute_script("return document.body.scrollHeight")
    # while scrl_cnt < 2:
    #     web.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(SCROLL_PAUSE_TIME)
    #     new_height = web.execute_script("return document.body.scrollHeight")
    #     if new_height == last_height:
    #         break
    #     last_height = new_height
    #     scrl_cnt += 1
    # section = wait_and_grab(web,By.ID,"Search Results").find_element(By.CSS_SELECTOR,".StackChildren__StyledStackChildren-sc-1tveqpz-0.gaitAv.sc-8d83c7bd-2.sc-9ece2aec-2.jopAQE.eIMErN")
    # sections = section.find_elements(By.XPATH,"*")
    # print(len(sections))
    # rec_restaurants = sections[2]
    time.sleep(30)
    restaurants_lst = web.find_elements(By.CSS_SELECTOR,".sc-8d83c7bd-1.sc-e201b5cf-0.sc-2dec7c95-0.cQPKtK.dVIWQb.cAvxvr")
    if len(restaurants_lst)<1:
        print("no restaurants retrying")
        restaurants_lst = web.find_elements(By.CSS_SELECTOR,".sc-8d83c7bd-1.sc-e201b5cf-0.sc-2dec7c95-0.cQPKtK.kXJLqA.TvPiX")
    # try:
    #     restaurants = sections[0]
    #     restaurants_lst = restaurants_lst+ restaurants.find_elements(By.XPATH,"*")
    # except:
    #     print("no rec restaurants")
    cnt = 0
    open_stores = []
    for restaurant in restaurants_lst:
        cnt += 1
        print(cnt)
        try:
            desc = restaurant.text.split("\n")
            if desc[3] == "Closed":
                print("closed")
                pass
            if desc[-1] == "Sponsored":
                print("dup")
                pass
            else:
                open_stores.append(restaurant)
                print(desc)
        except:
            print("fail")
    valid_restaurants = []
    restaurant_class_lst = []
    urls = []
    for restaurant in open_stores:
        url = restaurant.find_element(By.TAG_NAME,"a").get_attribute("href")
        if url[25:37] == "convenience/":
            print("convinience store")
            pass
        else:
            valid_restaurants.append(restaurant)
            urls.append(url)
    print(urls)
    threads = []
    total_thread_cnt = len(urls)
    active_threads = 3
    url_cnt = 0
    while total_thread_cnt > 0:
        thread_cnt = total_thread_cnt
        if total_thread_cnt > active_threads:
            thread_cnt = active_threads
        total_thread_cnt -= thread_cnt
        for i in range(thread_cnt):
            desc = valid_restaurants[url_cnt].text.split("\n")
            distance = float(desc[4].split(" ")[0])
            delivery_fee = float(desc[6].split(" ")[0][1:])
            clean_text = int(''.join(char for char in desc[2] if char.isalnum()))
            delivery_time = int(desc[6].split()[0])
            t = ScrapeThread(urls[url_cnt],food,Restaurant(desc[0],"","DD",float(desc[1]),distance,delivery_fee,clean_text,delivery_time))
            print(urls[url_cnt])
            t.start()
            threads.append(t)
            url_cnt += 1
        for t in threads:
            t.join()

dd_home_scrape("4820 201 st","chicken")
