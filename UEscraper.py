from browser import ue_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from FoodClasses import clean_int, clean_float, Restaurant, FoodItem
from browser import wait_and_grab, wait_and_grab_elms, wait_for_elem
from selenium.webdriver.common.keys import Keys
import time
import threading
import bs4

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
        #grab address
        self.restaurant.add_addr(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[3]/div/section/ul/button[1]/div[2]").text.replace("\n"," "))
        print(self.restaurant.addr)

        #uses search bar in menu
        # item_fld = wait_and_grab(driver,By.CSS_SELECTOR,".af.e5.d9.db.da.dc.dd.df.de.dg.dh.bh.il.jy.r4.nw.r5.r6.qy.qz.bo.em.bq.dw.b1.r7.r8")
        # driver.execute_script("arguments[0].scrollIntoView(true);", item_fld)
        # item_fld.send_keys(self.food)
        # item_fld.send_keys(Keys.ENTER)
        #DD unloads elements outside of screen so we must scroll through the page to load elements and add to our data
        #scrolls scrl_cnt amount of times through each menu and grabs all menu items
        # scrl_cnt = 0
        # scrl_max = 100
        # SCROLL_PAUSE_TIME = 0.5
        # # Get scroll height
        # last_height = driver.execute_script("return document.body.scrollHeight")
        #
        # while scrl_cnt<scrl_max:
        #     # Scroll down to bottom
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #
        #     # Wait to load page
        #     time.sleep(SCROLL_PAUSE_TIME)
        #
        #     # Calculate new scroll height and compare with last scroll height
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         break
        #     last_height = new_height
        #     scrl_cnt += 1
        # food_items = []
        # try:
        driver.execute_script("window.scrollBy(0, 2000);")
        container = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/main/div[6]/div/div/div/ul",20)
        print("container found")
        food_item_class = container.find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME, "div").find_element(
            By.TAG_NAME, "ul").find_element(By.TAG_NAME, "li").get_attribute("class")
        clean_class = ""
        for i in food_item_class.split(" "):
            clean_class += "."
            clean_class += i
        food_items = wait_and_grab_elms(web, By.CSS_SELECTOR, clean_class, 30)

        # except:
        #     print("no items present")
        print(len(food_items))
        for food_item in food_items:
            food_title = wait_and_grab(food_item, By.CSS_SELECTOR, ".is.im.it.dc.dd.de.df.b1").text
            try:
                food_desc = wait_and_grab(food_item, By.CSS_SELECTOR,".lx.kd.kf.ke.bb.p7.ex").text
            except:
                print("no descp")
                food_desc = ""
            food_price = clean_float(wait_and_grab(food_item, By.CSS_SELECTOR, ".lx.al.ca.hf").text)
            desc = food_item.text.split("\n")
            print(desc)
            try:
                image = wait_and_grab(food_item, By.CSS_SELECTOR, "[type='image/webp']", 1).get_attribute("srcset")
            except:
                print("image not found")
                image = "not found"
            # add fooditem to restaurant class
            self.restaurant.add_item(FoodItem(food_title, food_desc, food_price, image))
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
    restaurant_class_lst = []
    threads = []
    total_thread_cnt = len(urls)
    active_threads = 1
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
            desc = valid_restaurants[url_cnt].text.split("\n")
            print(desc)
            name = ""
            r = Restaurant(name, "", "DD", 0, 0, 0, 0, 0)
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
    for restaurant in restaurant_class_lst:
        print(restaurant)
ue_scrape("1970 158a st","chicken")