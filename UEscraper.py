from browser import ue_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from FoodClasses import clean_int, clean_float, Restaurant, FoodItem
from browser import wait_and_grab, wait_and_grab_elms, wait_for_elem
from selenium.webdriver.common.keys import Keys
import time
import threading

#Options for chrome webdriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")
web = webdriver.Chrome(options=options)
#worker threads for opening a chome tab and extracting all the menu items
class ScrapeThread(threading.Thread):
    def __init__(self, url,food,restaurant,adr):
        threading.Thread.__init__(self)
        self.url = url
        self.food = food
        self.restaurant = restaurant
        self.adr = adr

    def run(self):
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(1)
        loc_btn=wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/header/div/div/div/div/div/div[3]/div[2]/div")
        loc_btn.click()
        loc_fld = wait_and_grab(driver,By.CSS_SELECTOR,"[placeholder='Search for an address']")
        loc_fld.send_keys(self.adr)
        adr_btn = wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[2]/div/div/div[2]/div/div/div/div/ul/button")
        adr_btn.click()
        wait_for_elem(driver,By.CSS_SELECTOR,"[clip-rule='evenodd']")
        #grab rest name
        self.restaurant.name = wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[1]/div[3]/div/div/div[1]/h1").text
        #grab rest address
        self.restaurant.add_addr(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[3]/div/section/ul/button[1]/div[2]").text.replace("\n"," "))
        #grab rating
        try:
            self.restaurant.rating = clean_float(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[1]/div[3]/div/div/div[1]/div/p[1]/span[1]").text)
        except:
            print("no rating")
        #grab delivery fee
        self.restaurant.deliv_fee = clean_float(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]/div/div/p/span[2]").text)
        #grab delivery time
        self.restaurant.deliv_time = clean_int(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[2]/div[2]/div/div/div[3]/div/div/div/p[1]/span").text)
        #grab review count
        try:
            self.restaurant.review_count = clean_int(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[1]/div[3]/div/div/div[1]/div/p[1]/span[3]").text)
        except:
            print("no reviews")

        #grab
        food_items = []
        try:
            food_items = wait_and_grab_elms(driver, By.CSS_SELECTOR, '[data-test^="store-item"]', 30)
        except:
            print("no items present")
        print(len(food_items))
        for food_item in food_items:
            has_price = True
            has_discnt = False
            desc = food_item.text.split("\n")
            print(desc)
            descs = food_item.find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_elements(By.XPATH,"*")
            food_desc = ""
            food_price = 0
            discnt = ""
            food = None
            food_title = descs[0].text
            try:
                food_price = clean_float(descs[1].text)
            except:
                print("no price")
                has_price = False
            try:
                discnt_test = descs[2].find_element(By.TAG_NAME,"span").value_of_css_property("color")
                if discnt_test == "#0E8345":
                    discnt = descs[2].text
                print(discnt," discountm")
            except:
                print("no discount")
            if not has_discnt:
                try:
                    food_desc = descs[2].text
                except:
                    print("no desc")
                try:
                    discnt = descs[3].text
                except:
                    print("no discount")
            try:
                image = food_item.find_element(By.TAG_NAME, "source").get_attribute("srcset")
            except:
                print("image not found")
                image = "not found"
            # add fooditem to restaurant class
            if has_price:
                food = FoodItem(food_title, food_desc, food_price, image)
                self.restaurant.add_item(food)
            if has_discnt:
                self.restaurant.add_discount(discnt,food)
        print(self.restaurant.name+" has this many items: ",len(self.restaurant.catalogue))
        driver.close()
def ue_scrape(adr,food):
    ue_init(adr,web)
    srch_fld = wait_and_grab(web,By.ID,"search-suggestions-typeahead-input")
    srch_fld.send_keys(food)
    srch_fld.send_keys(Keys.ENTER)
    try:
        wait_for_elem(web,By.CSS_SELECTOR,".bo.fx.cr.br.cp",10)
    except:
        wait_for_elem(web,By.CSS_SELECTOR,".bo.id.dv.br.hk")
    restaurant_lst = wait_and_grab(web,By.CSS_SELECTOR,"[data-testid='feed-desktop']").find_elements(By.XPATH,"*")
    print(len(restaurant_lst))
    valid_restaurants = []
    urls = []
    for restaurant in restaurant_lst:
        desc = restaurant.text
        print(desc.split("\n"))
        if "Pick it up" in desc:
            print("pick up only")
            pass
        elif "Closed" in desc:
            print("closed")
            pass
        else:
            valid_restaurants.append(restaurant)
            urls.append(wait_and_grab(restaurant,By.TAG_NAME,"a").get_attribute("href"))
    rest_cnt = len(urls)
    if rest_cnt>20:
        rest_cnt = 20
    restaurant_class_lst = []
    threads = []
    total_thread_cnt = rest_cnt
    active_threads = 2
    url_cnt = 0
    # total thread cnt indicates how many threads we need to run in total to go through all restaurants
    # it will create active_threads amount of workers each time to open a browser and grabs the menu item in parallel
    while total_thread_cnt > 0:
        # calculates how many threads to use
        thread_cnt = total_thread_cnt
        if total_thread_cnt > active_threads:
            thread_cnt = active_threads
        total_thread_cnt -= thread_cnt
        # parses the restaurant description and creates the restaurant class
        for i in range(thread_cnt):
            print(i)
            desc = valid_restaurants[url_cnt].text.split("\n")
            print(desc)
            name = ""
            r = Restaurant(name, "", "UE", 0, 0, 0, 0, 0)
            restaurant_class_lst.append(r)
            # creates the workers
            t = ScrapeThread(urls[url_cnt], food, r,adr)
            print(urls[url_cnt])
            t.start()
            threads.append(t)
            url_cnt += 1
        # joins the workers
        for t in threads:
            t.join()
    restaurant_class_lst.pop(-1)
    for restaurant in restaurant_class_lst:
        print(restaurant)
ue_scrape("1970 158a st","chicken")