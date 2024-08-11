from __future__ import annotations
from typing import Any, Optional
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def wait_for_elem(web_elem, search_type: str, search_val: str, timeout = 5):
    """ Wait until an element is available, but do not return it.

    :param web_elem:
    :param search_type:
    :param search_val:
    :param timeout:
    :return:
    """
    wait = WebDriverWait(web_elem, timeout)
    wait.until(ec.presence_of_element_located((search_type, search_val)))


def wait_and_grab(web_elem, search_type: str, search_val: str, timeout = 5) -> webelement.WebElement:
    """ Wait until an element is available and return it once it's found.

    :param web_elem:
    :param search_type:
    :param search_val:
    :param timeout:
    :return:
    """
    wait_for_elem(web_elem, search_type, search_val, timeout)

    return web_elem.find_element(search_type, search_val)


def wait_and_grab_elms(web_elem, search_type: str, search_val: str, timeout = 10) -> list[webelement.WebElement]:
    """ Wait until an element is available and return it once it's found.

    :param web_elem:
    :param search_type:
    :param search_val:
    :param timeout:
    :return:
    """
    wait_for_elem(web_elem, search_type, search_val, timeout)

    return web_elem.find_elements(search_type, search_val)

#inputs location into skip
def sd_init(adr,web):
    web.get("https://www.skipthedishes.com/")

    adr_fld = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div/input")
    adr_fld.send_keys(adr)

    adr_btn = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[1]/div/div[2]/ul/li[1]/button")
    adr_btn.click()

    adr_conf_btn = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[3]/button")
    adr_conf_btn.click()

#inputs location and item into doordash
def dd_init(adr,food,web):
    web.get("https://www.doordash.com/search/store/"+food.replace(" ", "%20"))
    #current workaround is to disable custom locations and use the defualt locatiom
    # loc_btn = wait_and_grab(web, By.CSS_SELECTOR, ".styles__ButtonRoot-sc-1nqx07s-0.ixDTkG")
    # loc_btn.click()
    #
    # adr_fld = web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div[1]/div/div/div[2]/div/div[2]/input")
    # adr_fld.send_keys(adr)
    #
    # adr_lst = wait_and_grab(web, By.ID, "addressAutocompleteDropdown")
    #
    # adr_btn = adr_lst.find_element(By.TAG_NAME,"span")
    # print(adr_btn.text)
    # adr_btn.click()
    #
    # try:
    #     save_btn = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div[1]/div/main/div[2]/div/div/div[2]/div/div/div[1]/div/div/div[5]/button[2]")
    # except:
    #     save_btn = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div[1]/div/main/div[2]/div/div/div[2]/div/div/div[1]/div/div/div[6]/button[2]")
    # save_btn.click()

#input location into uber eats
#may break in future? works for now tho
def ue_init(adr,web):
    web.get("https://www.ubereats.com/")

    loc_btn = wait_and_grab(web, By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[1]/div/div[1]/div/div/input")
    loc_btn.send_keys(adr)

    adr_lst = wait_and_grab(web, By.ID, "location-typeahead-home-menu")

    adr_btn = wait_and_grab(adr_lst, By.TAG_NAME, "li")
    adr_btn.click()


#when calling the functions make sure to space out the address and add the city for the adr param
#the web param is meant for the webdriver
#for food in dd_init just put in the string for what food to search
if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    web = webdriver.Chrome(options=options)
    sd_init("4820 201 st",web)
    dd_init("4820 201 st","chicken",web)
    ue_init("4820 201 st langley",web)
