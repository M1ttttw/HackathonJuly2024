from __future__ import annotations
from typing import Any, Optional
import threading
from browser import sd_init
from browser import wait_and_grab, wait_for_elem
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from FoodClasses import Restaurant, FoodItem, clean_int, clean_float
import time
from GPT import acquire_calories


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

        # Start a new driver set to our new rest_url_w_food
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        rest_driver = webdriver.Chrome(options=options)
        rest_driver.get(f"{self.url}?search={self.food.replace(' ', '%20')}")

        # We also need to grab the text that describes the restaurant's address
        rest_addr = wait_and_grab(rest_driver, By.XPATH, '//*[@id="root"]/div/main/div/div/div/div[1]/div/div[2]/'
                                                        'div/div/div/div[2]/div[1]/span/span[2]/p').text
        self.restaurant.add_addr(rest_addr)
        # Convenience store pages are very different, take advantage of this!
        try:
            wait_and_grab(rest_driver,By.CSS_SELECTOR,"[placeholder='Search Store']")
            print("Convenience Store Detected")
            rest_driver.close()
        except:
            pass
        try:
            # Find the container containing the subdivisions of a menu
            mega_container = wait_and_grab(rest_driver, By.XPATH, '//*[@id="ComponentsContainer"]/div')
        except:
            print("Convenience Store Detected")
            rest_driver.close()



        addr_entered = False
        item_list = rest_driver.find_elements(By.CSS_SELECTOR,".styles__ListItem-sc-120s71t-3.fpnvFo")
            # # We then iterate through the items in that subdivision.
        if len(item_list) > 150:
            # print(self.restaurant.name," too many items")
            rest_driver.close()
            return
        for item in item_list:
            try:
                item_name = item.find_element(By.CSS_SELECTOR,'[itemprop="name"]').text
            except:
                continue
            # Skip over any items that have no children
            # item_children = item.find_elements(By.XPATH, "*")

            # Then grab everything you need about the food item
            price_info = item.find_element(By.TAG_NAME,"h4").text

            # It's possible for the item to be sold out, so check for it, and skip over it if needed
            if price_info == "SOLD OUT":
                print("Item sold out")
                continue

            if price_info == "See Item":
                # Open the item in view, and grab the price
                # print("Found a see item")
                item.click()

                # Check if you ever entered your address before
                if not addr_entered:
                    # Grab the text field for putting your address
                    addr_fld = wait_and_grab(rest_driver, By.XPATH,
                                             "/html/body/div[2]/div/div[1]/div/header/div/div/div[1]/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div[2]/div/div/div/div/div[1]/div[2]/form/input",
                                             30)
                    addr_fld.send_keys(self.adr)

                    # Grab the first address that pops up
                    addr_elem = wait_and_grab(rest_driver, By.XPATH,
                                              "/html/body/div[2]/div/div[1]/div/header/div/div/div[1]/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div[2]/div/div/div/div[1]/div[2]/div/div/div[1]",
                                              30)
                    addr_elem.click()

                    submit_btn = wait_and_grab(rest_driver, By.XPATH,
                                               "/html/body/div[2]/div/div[1]/div/header/div/div/div[1]/div[2]/div/div[2]/div[1]/div/div/div/div[3]/div[2]/div/div/div/div[4]/button",
                                               30)
                    submit_btn.click()

                    addr_entered = True
                    wait_for_elem(rest_driver, By.XPATH,
                                  '//*[@id="container"]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div[1]/div[2]')
                    item.click()

                # Grab the price
                close_btn = wait_and_grab(rest_driver, By.CSS_SELECTOR,
                                          ".MuiButtonBase-root.MuiIconButton-root.styles__StyledIconButton-sc-nhn5sv-0.cHIlwY",
                                          20)
                item_price = float(
                    rest_driver.find_element(By.CSS_SELECTOR, ".styles__Right-sc-gvk0sj-3.ixLLwq").text[1:])

                action = ActionChains(rest_driver)
                action.move_to_element(close_btn).click().perform()

            else:
                item_price = clean_float(price_info)

            # Some item's don't have descriptions, so we need to take that into account

            try:
                item_desc = item.find_element(By.CSS_SELECTOR,'[itemprop="description"]').text
            except:
                item_desc = ""


            # print(item_name, item_desc, item_price)

            # We attempt to grab the image of the item. there are 3 cases we handle
            try:
                # Case 1: Big image is being used to showcase the item, thus the html shifts around
                item_img = item.find_element(By.XPATH, ".//div/div[1]/div/div[1]/div/img").get_attribute("src")
            except:
                try:
                    # Case 2: A smaller thumbnail image is being used to showcase the item.
                    item_img = item.find_element(By.XPATH,
                                                 ".//div/div[1]/div/div/div[2]/div/div/img").get_attribute("src")
                except:
                    # Case 3: It just has no image at all...
                    item_img = ""

            # Create a new food item with the stored info
            food_item = FoodItem(item_name, item_desc, item_price, item_img)

            # Add this new food item to the restaurant
            self.restaurant.add_item(food_item)
        try:
            discnt = rest_driver.find_element(By.CSS_SELECTOR, ".styles__OfferTxt-sc-wnmoxv-2.jyTFiJ").text
            self.restaurant.add_discount(discnt)
        except:
            print("no discount")
            # Once we are done with the restaurant, close the webdriver and add the restaurant
        rest_driver.close()



def sd_rest_scrape(addr, food):
    # Create a new web driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    web = webdriver.Chrome(options=options)

    # Navigate web driver to home page
    sd_init(addr, web)

    # Input the food into the search bar
    search_field = web.find_element(By.XPATH, '//*[@id="header-search"]')
    search_field.send_keys(food)

    # Wait and grab the food in items button
    items_button = wait_and_grab(web, By.XPATH, '//*[@id="root"]/div/div[1]/div/header/div/'
                                                'div/div[2]/div[3]/div[2]/div/button')
    items_button.click()

    # Next, we want to wait and find the restaurant list
    try:
        wait_for_elem(web, By.XPATH, '//*[@id="root"]/div/main/div/div/div/div/ul/li[1]/div/div[1]/div/a')
    except:
        # If we time out, we return nothing as there may be a chance that no restaurants showed up...
        return []
    rests_parent = wait_and_grab(web, By.XPATH, "/html/body/div[2]/div/main/div/div/div/div/ul")
    rests_UI_list = rests_parent.find_elements(By.XPATH, "*")
    urls = []
    for rest in rests_UI_list:
        rest_url = wait_and_grab(rest, By.XPATH, ".//div/div[1]/a").get_attribute("href")
        urls.append(rest_url)
    return [rests_UI_list,urls,web]
    # print(f"there are {len(rests_UI_list)} restaurants currently in view")
def sd_menu_scrape(addr,food,rests_UI_list,urls,timeout=15):
    # Keep a counter to go through a limited number of restaurant.
    rest_list = []
    active_threads = 2
    total_thread_cnt = len(rests_UI_list)
    threads = []
    url_cnt = 0
    # total thread cnt indicates how many threads we need to run in total to go through all restaurants
    # it will create active_threads amount of workers each time to open a browser and grabs the menu item in parallel
    while total_thread_cnt>0:
        # calculates how many threads to use
        thread_cnt = total_thread_cnt
        if total_thread_cnt > active_threads:
            thread_cnt = active_threads
        total_thread_cnt -= thread_cnt
        for i in range(thread_cnt):
            # print(i)
            rest_UI = rests_UI_list[url_cnt]
            rest_url = urls[url_cnt]
            # Grab the url of the restaurant we want to check out

            # print(rest_url)

            # We need to know the restaurant's information, thus, we grab the restaurant's info
            rest_info = rest_UI.text.split("\n")
            rest_name, rest_deliv_time_str, rest_deliv_fee_str, rest_rate = (rest_info[0], rest_info[1], rest_info[2],
                                                                             float(rest_info[3]))

            # Cut out the fat in rest_deliv_time_str
            rest_deliv_time_split = rest_deliv_time_str.split(" ")
            rest_deliv_time = (int(rest_deliv_time_split[2]) + int(rest_deliv_time_split[0])) / 2

            # Cut out the fat in rest_deliv_fee_str
            rest_deliv_fee_split = rest_deliv_fee_str.split(" ")
            rest_deliv_fee = float(rest_deliv_fee_split[0][1:])
            try:
                rest_img = rest_UI.find_element(By.TAG_NAME,"img").get_attribute("src")
            except:
                rest_img = ""
            # print(f"{rest_name}, {rest_deliv_time}, {rest_deliv_fee}, {rest_rate}")
            rest = Restaurant(rest_name, "", "SkipTheDishes", rest_rate, -1, rest_deliv_fee, -1,
                              rest_deliv_time, rest_url,rest_img)
            # creates the workers
            t = ScrapeThread(rest_url, food, rest, addr)
            t.start()
            threads.append(t)
            rest_list.append(rest)
            url_cnt += 1
        #joins the workers
        for t in threads:
            t.join(timeout)
            # kills thread if it exceeds timeout
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
        time.sleep(0.5)
    # print(f"Successfully Went through {rest_count} stores")
    # removes restaurants with empty menus
    i = 0
    while i < len(rest_list):
        restaurant = rest_list[i]
        # print(restaurant)
        if len(restaurant.catalogue) < 1:
            rest_list.pop(i)
        else:
            # acquire_calories(restaurant, 25)
            i += 1
    # Return our results!
    return rest_list


# if __name__ == "__main__":
#     test_addr = "9937 157 St"
#     test_food = "Chicken"
#     test_limit = 2
#
#     # This is a test
#     start_time = time.time()
#     rest_lst = sd_home_scrape(test_addr, test_food, test_limit)
#     end_time = time.time()
#     # print(f"Test took {end_time - start_time} seconds for {test_limit} restaurants")
#
#     for rest in rest_lst:
#         for food_name in rest.catalogue:
#             food_item = rest.catalogue[food_name]
#             # print(f"{food_item.name} has {food_item.calories} calories and a cpd of {food_item.cpd}")

