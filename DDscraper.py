from browser import dd_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from FoodClasses import Restaurant
import time
import threading

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
web = webdriver.Chrome(options=options)



class ScrapeThread(threading.Thread):
    def __init__(self, url,food):
        threading.Thread.__init__(self)
        self.url = url
        self.food = food

    def run(self):
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        scrl_cnt = 0
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        while scrl_cnt < 5:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrl_cnt += 1
        item_fld = driver.find_element(By.ID,"item-search-field")
        item_fld.send_keys(self.food)
        categories = driver.find_elements(By.CSS_SELECTOR,".sc-75da66f4-0.jvBEhF")
        food_items = []
        for category in categories:
            food_items = food_items + category.find_element(By.CSS_SELECTOR, ".sc-234bce1d-0.cbmNka").find_element(By.TAG_NAME, "div").find_elements(By.TAG_NAME, "div")
        driver.close()
        print(len(food_items))
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
    active_threads = 5
    url_cnt = 0
    while total_thread_cnt > 0:
        thread_cnt = total_thread_cnt
        if total_thread_cnt > active_threads:
            thread_cnt = active_threads
        total_thread_cnt -= thread_cnt
        for i in range(thread_cnt):
            t = ScrapeThread(urls[url_cnt],food)
            print(urls[url_cnt])
            t.start()
            threads.append(t)
            url_cnt += 1
        for t in threads:
            t.join()

dd_home_scrape("4820 201 st","chicken")
