from browser import ue_init
from selenium import webdriver
from selenium.webdriver.common.by import By
from FoodClasses import clean_int, clean_float, Restaurant, FoodItem
from browser import wait_and_grab, wait_and_grab_elms, wait_for_elem
from selenium.webdriver.common.keys import Keys
from GPT import acquire_calories
import time
import threading


#worker threads for opening a chome tab and extracting all the menu items
class ScrapeThread(threading.Thread):
    def __init__(self, url,food,restaurant,adr):
        threading.Thread.__init__(self)
        self.url = url
        self.food = food
        self.restaurant = restaurant
        self.adr = adr
    def kill(self):
        raise Exception
    def run(self):
        # Options for chrome webdriver
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        time.sleep(1)
        #input location
        loc_btn=wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/header/div/div/div/div/div/div[3]/div[2]/div")
        loc_btn.click()
        loc_fld = wait_and_grab(driver,By.CSS_SELECTOR,"[placeholder='Search for an address']")
        loc_fld.send_keys(self.adr)
        adr_btn = wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[2]/div/div/div[2]/div/div/div/div/ul/button")
        adr_btn.click()
        wait_for_elem(driver,By.CSS_SELECTOR,"[clip-rule='evenodd']")
        #grab rest address
        try:
            self.restaurant.add_addr(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[3]/div/section/ul/button[1]/div[2]").text.replace("\n"," "))
        except:
            print("no address")
        #grab delivery fee
        try:
            self.restaurant.deliv_fee = clean_float(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[2]/div[2]/div/div/div[1]/div/div/p/span[2]").text)
        except:
            print("no delivery fee")
        #grab review count
        try:
            self.restaurant.review_count = clean_int(wait_and_grab(driver,By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[1]/div[3]/div/div/div[1]/div/p[1]/span[3]").text)
        except:
            print("no reviews")

        #grab food items
        food_items = []
        try:
            food_items = wait_and_grab_elms(driver, By.CSS_SELECTOR, '[data-test^="store-item"]', 30)
        except:
            print("no items present")
        # print(len(food_items))
        # for each food item, grab their relative info
        for food_item in food_items:
            has_price = True
            has_discnt = False
            #grab and seperate item description
            desc = food_item.text.split("\n")
            # print(desc)
            #grab item description
            descs = food_item.find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_element(By.XPATH,"*").find_elements(By.XPATH,"*")
            food_desc = ""
            food_price = 0
            discnt = ""
            food = None
            food_title = descs[0].text
            #grabs food price
            try:
                food_price = clean_float(descs[1].text)
            except:
                # print("no price")
                has_price = False
                continue
            #test for discount
            try:
                #if text color is green then grab it
                discnt_test = descs[2].find_element(By.TAG_NAME,"span").value_of_css_property("color")
                if discnt_test == "rgba(14, 131, 69, 1)":
                    discnt = descs[2].find_element(By.TAG_NAME,"span").text
                if len(discnt) > 0:
                    has_discnt = True
                    # print(discnt_test,discnt," discountm")
            except:
                pass
                # print("no discount")
            #if third section is not discount then it is description
            if not has_discnt:
                # try to grab description
                try:
                    food_desc = descs[2].text
                except:
                    pass
                    # print("no desc")
                #if the third section is not discount and there exists a fourth section then it is discount
                try:
                    discnt = descs[3].text
                    discnt_clr = descs[3].find_element(By.TAG_NAME,"span").value_of_css_property("color")
                    if len(discnt) > 0:
                        has_discnt = True
                        # print(discnt,discnt_clr," discountm2")

                except:
                    pass
                    # print("no discount")
            #try to grab image url
            try:
                image = food_item.find_element(By.TAG_NAME, "source").get_attribute("srcset")
            except:
                # print("image not found")
                image = ""
            # add fooditem to restaurant class
            if has_price:
                food = FoodItem(food_title, food_desc, food_price, image)
                self.restaurant.add_item(food)
            # if there is discount then add it
            if has_discnt:
                self.restaurant.add_discount(discnt,food)
        #if restuarant has banner discount then add it
        try:
            banner_discnt = driver.find_element(By.CSS_SELECTOR,'[data-testid="eater-message-card"]').text
            self.restaurant.add_discount(banner_discnt)
        except:
            pass
            # print("no banner discnt")
        # print(self.restaurant.name+" has this many items: ",len(self.restaurant.catalogue))
        driver.close()
def ue_rest_scrape(adr,food):
    # Options for chrome webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    web = webdriver.Chrome(options=options)

    # Hacky Fix involving rerunning ue_init for odd timeouts.
    i = 0
    ret_init = ue_init(adr,web)
    while ret_init == -2 and i < 5:
        ret_init = ue_init(adr, web)
        i += 1

    #searches food in search bar
    srch_fld = wait_and_grab(web,By.ID,"search-suggestions-typeahead-input")
    srch_fld.send_keys(food)
    srch_fld.send_keys(Keys.ENTER)
    # grabs all restaurants
    restaurant_lst = wait_and_grab(web, By.CSS_SELECTOR, "[data-testid='feed-desktop']").find_elements(By.XPATH, "*")
    # print(len(restaurant_lst))
    valid_restaurants = []
    urls = []
    # get rid of all closed/pickup only restaurant
    for restaurant in restaurant_lst:
        desc = restaurant.text
        # print(desc.split("\n"))
        if "Pick it up" in desc:
            print("pick up only")
            pass
        elif "Closed" in desc:
            print("closed")
            pass
        else:
            valid_restaurants.append(restaurant)
            urls.append(wait_and_grab(restaurant, By.TAG_NAME, "a").get_attribute("href"))
    return [valid_restaurants,urls,web]

def ue_menu_scrape(adr,food,valid_restaurants,urls,timeout=25):
    restaurant_class_lst = []
    threads = []
    total_thread_cnt = len(urls)
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
            # print(total_thread_cnt)
            desc = valid_restaurants[url_cnt].text.split("\n")
            # print(desc)
            name = desc[0]
            try:
                rating = clean_float(desc[-2])
            except:
                rating = -1
            try:
                rest_img = valid_restaurants[url_cnt].find_element(By.TAG_NAME, "source").get_attribute("srcset")
            except:
                rest_img = ""
            r = Restaurant(name, "", "UE", rating, -1, -1, -1, clean_int(desc[-1]),urls[url_cnt],rest_img)
            restaurant_class_lst.append(r)
            # creates the workers
            t = ScrapeThread(urls[url_cnt], food, r,adr)
            # print(urls[url_cnt])
            t.start()
            threads.append(t)
            url_cnt += 1
        # joins the workers
        for t in threads:
            t.join(timeout)
            #kills thread if it exceeds timeout
            if t.is_alive():
                print("timeout")
                try:
                    t.kill()
                except:
                    print("thread killed")
    is_alive = False
    for t in threads:
        if t.is_alive():
            is_alive = True
    while is_alive:
        is_alive = False
        for t in threads:
            if t.is_alive():
                is_alive = True
                try:
                    t.kill()
                except:
                    print("thread killedX2")
        time.sleep(0.5)
    banned_urls = []
    #removes restaurants with empty menus
    l = len(restaurant_class_lst)
    p = 0
    while (p < l):
        restaurant = restaurant_class_lst[p]
        # print(restaurant)
        if len(restaurant.catalogue) < 1:
            restaurant_class_lst.remove(restaurant)
            banned_urls.append(restaurant.url)
            p -= 1
            l -= 1
        else:
            acquire_calories(restaurant, 100, 32768)
        p += 1
    return [restaurant_class_lst, banned_urls]


# if __name__ == "__main__":
#     start_time = time.time()
#     ue_scrape("1970 158a st","chicken",10)
#     end_time = time.time()
#     print(f"Test took {end_time - start_time} seconds for 10 restaurants")
