from selenium import webdriver
import time
from selenium.webdriver.common.by import By


#inputs location into skip
def sd_init(adr,web):
    web.get("https://www.skipthedishes.com/")
    time.sleep(5)
    adr_fld = web.find_element(By.XPATH,"/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div/input")
    adr_fld.send_keys(adr)
    time.sleep(2)
    adr_btn = web.find_element(By.XPATH,"/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[1]/div/div[2]/ul/li[1]/button")
    adr_btn.click()
    time.sleep(2)
    adr_conf_btn = web.find_element(By.XPATH,"/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[3]/button")
    adr_conf_btn.click()
    time.sleep(5)
#inputs location and item into doordash
def dd_init(adr,food,web):
    web.get("https://www.doordash.com/search/store/"+food)
    time.sleep(10)
    loc_btn = web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[1]/div/div[1]/div[1]/div/div/div[1]/header/div[2]/div[2]/div[2]/div/div/button")
    loc_btn.click()
    adr_fld = web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div[1]/div/div/div[2]/div/div[2]/input")
    adr_fld.send_keys(adr)
    time.sleep(2)
    adr_lst = web.find_element(By.ID,"addressAutocompleteDropdown")
    adr_btn = adr_lst.find_element(By.TAG_NAME,"span")
    print(adr_btn.text)
    adr_btn.click()
    time.sleep(3)
    try:
        save_btn = web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[2]/div/div/div[2]/div/div/div[1]/div/div/div[5]/button[2]")
    except:
        save_btn = web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[2]/div/div/div[2]/div/div/div[1]/div/div/div[6]/button[2]")
    save_btn.click()
    time.sleep(5)
#input location into uber eats
#may break in future? works for now tho
def ue_init(adr,web):
    web.get("https://www.ubereats.com/")
    time.sleep(3)
    loc_btn = web.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[1]/div/div[1]/div/div/input")
    loc_btn.send_keys(adr)
    time.sleep(3)
    adr_lst = web.find_element(By.ID,"location-typeahead-home-menu")
    adr_btn = adr_lst.find_element(By.TAG_NAME,"li")
    adr_btn.click()
    time.sleep(5)


#when calling the functions make sure to space out the address and add the city for the adr param
#the web param is meant for the webdriver
#for food in dd_init just put in the string for what food to search
# sd_init("4820 201 st",web)
# dd_init("4820 201 st","chicken",web)
# ue_init("4820 201 st langley",web)
