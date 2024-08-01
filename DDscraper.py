from browser import dd_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from FoodClasses import clean_int
from FoodClasses import clean_float
from FoodClasses import Restaurant
from FoodClasses import FoodItem
from browser import wait_and_grab
from browser import wait_and_grab_elms
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
    def __init__(self, url,food,restaurant):
        threading.Thread.__init__(self)
        self.url = url
        self.food = food
        self.restaurant = restaurant

    def run(self):
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(1)
        #grab address
        self.restaurant.add_addr(wait_and_grab(driver,By.CSS_SELECTOR,".Text-sc-16fu6d-0.hNVOUs").text+" "+wait_and_grab(driver,By.CSS_SELECTOR,".Text-sc-16fu6d-0.kVKROG").text)
        #uses search bar in menu
        item_fld = wait_and_grab(driver,By.ID,"item-search-field")
        driver.execute_script("arguments[0].scrollIntoView(true);", item_fld)
        item_fld.send_keys(self.food)
        item_fld.send_keys(Keys.ENTER)
        #DD unloads elements outside of screen so we must scroll through the page to load elements and add to our data
        #scrolls scrl_cnt amount of times through each menu and grabs all menu items
        scrl_cnt = 5
        cnt = 0
        while cnt < scrl_cnt:
            time.sleep(1)
            #try to grab all the menu items. if none are present then that means we are at the bottom and we can break the loop
            try:
                food_items = wait_and_grab_elms(driver,By.CSS_SELECTOR, ".sc-234bce1d-2.hAZmjs",5)
            except:
                print("no items present")
                break
            #loop through all items we scanned and extract the title, description ... etc
            for food_item in food_items:
                food_title = wait_and_grab(food_item,By.CSS_SELECTOR,"[data-telemetry-id='storeMenuItem.title']").text
                try:
                    food_desc = wait_and_grab(food_item,By.CSS_SELECTOR,"[data-telemetry-id='storeMenuItem.subtitle']").text
                except:
                    print("no descp")
                    food_desc = ""
                food_price_raw = wait_and_grab(food_item,By.CSS_SELECTOR,"[data-anchor-id='StoreMenuItemPrice']").text
                if food_price_raw[-1] == "+":
                    food_price = float(
                        food_price_raw[3:-1])
                elif len(food_price_raw.split(" "))>1:
                    food_price = food_price_raw.split(" ")[0][3:]
                else:
                    food_price = food_price_raw[3:]

                desc = food_item.text.split("\n")
                print(desc)
                try:
                    image = wait_and_grab(food_item,By.TAG_NAME,"source",1).get_attribute("srcset").split(" ")[0]
                except:
                    print("image not found")
                    image = "not found"
                #add fooditem to restaurant class
                self.restaurant.add_item(FoodItem(food_title,food_desc,food_price,image))
            #scrolls
            driver.execute_script("window.scrollBy(0,1000);")
            cnt += 1
        print(self.restaurant.name+" has this many items: ",len(self.restaurant.catalogue))
        driver.close()

#main scraper
def dd_home_scrape(adr,food):
    #inits the doordash window
    dd_init(adr,food,web)
    #wait for a a specific icon that is the last in the loading order which indicates that the rest of the site is loaded
    wait_and_grab(web,By.CSS_SELECTOR,".styles__StyledInlineSvg-sc-1hetb2e-0.eCVqVv.fetched-icon",20)
    #for some reason doordash alternates between the classes sometimes so this is a hacky workaround
    #grabs all the elements of this class which are restaurants
    try:
        restaurants_lst = wait_and_grab_elms(web,By.CSS_SELECTOR,".sc-8d83c7bd-1.sc-e201b5cf-0.sc-2dec7c95-0.cQPKtK.dVIWQb.cAvxvr")
    except:
        restaurants_lst = web.find_elements(By.CSS_SELECTOR,".sc-8d83c7bd-1.sc-e201b5cf-0.sc-2dec7c95-0.cQPKtK.kXJLqA.TvPiX")
    #parse through all the items to get rid of any closed, duplicate or none restaurant elements
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
    #loop through again to remove all the convinience stores
    #also save the urls to the store page
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
    #create active_threads amount of worker threads to each open a browser to scroll through and collect all the menu datas
    #WARNING: THIS IS COMPUTATIONALLY EXPENSIVE AND ONLY INCREASE ACTIVE THREADS IF YOU HAVE GOOD COMPUTER
    threads = []
    total_thread_cnt = len(urls)
    active_threads = 2
    url_cnt = 0
    #total thread cnt indicates how many threads we need to run in total to go through all restaurants
    #it will create active_threads amount of workers each time to open a browser and grabs the menu item in parallel
    while total_thread_cnt > 0:
        # calculates how many threads to use
        thread_cnt = total_thread_cnt
        if total_thread_cnt > active_threads:
            thread_cnt = active_threads
        total_thread_cnt -= thread_cnt
        #parses the restaurant description and creates the restaurant class
        for i in range(thread_cnt):
            desc = valid_restaurants[url_cnt]
            name = wait_and_grab(desc,By.CSS_SELECTOR,".Text-sc-16fu6d-0.sc-a488a75b-20.bunCMC").text
            rating = clean_float(wait_and_grab(desc,By.CSS_SELECTOR,".InlineChildren__StyledInlineChildren-sc-nu44vp-0.VlCPZ").text)
            distance = clean_float(wait_and_grab(desc,By.CSS_SELECTOR,".InlineChildren__StyledInlineChildren-sc-nu44vp-0.iImEHZ").text)
            delivery_fee = clean_float(wait_and_grab(desc,By.CSS_SELECTOR,"[data-testid='STORE_TEXT_PRICING_INFO']").text)
            rev_cnt = clean_int(wait_and_grab(desc,By.CSS_SELECTOR,".InlineChildren__StyledInlineChildren-sc-nu44vp-0.cZhUKR.sc-3b51c52-0.hNbRoa").text[4:])
            delivery_time = clean_int(wait_and_grab(desc,By.CSS_SELECTOR,".InlineChildren__StyledInlineChildren-sc-nu44vp-0.iImEHZ").text)
            r = Restaurant(name, "", "DD", rating, distance, delivery_fee, rev_cnt, delivery_time, urls[url_cnt])
            try:
                discount = valid_restaurants[url_cnt].find_element(By.CSS_SELECTOR,".sc-a488a75b-0.dHRtoo").text
                r.add_disc(discount)
            except:
                pass
            restaurant_class_lst.append(r)
            #creates the workers
            t = ScrapeThread(urls[url_cnt],food,r)
            print(urls[url_cnt])
            t.start()
            threads.append(t)
            url_cnt += 1
        #joins the workers
        for t in threads:
            t.join()
    for restaurant in restaurant_class_lst:
        print(restaurant)

dd_home_scrape("4820 201 st","chicken")
