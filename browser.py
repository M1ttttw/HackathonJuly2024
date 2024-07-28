from selenium import webdriver
from webdrivermanager.chrome import ChromeDriverManager
import time
import random
from selenium.webdriver.common.by import By
import requests
from selenium_stealth import stealth
from bs4 import BeautifulSoup


#USELESS but still may be useful so i keep around{
#dd login
dd_email = "g5ctz.test@inbox.testmail.app"
dd_pw = "Hackathon2024"
dd_cell = "3434804602"
#skip login
sd_email = "g5ctz.test@inbox.testmail.app"
sd_pw = "@Hackathon2024"
sd_cell = "3434804602"
sd_num = "56XXX"

#for acc creation
og_email = "g5ctz.test@inbox.testmail.app"
# sms_site = "https://smstome.com/country/canada"
sms = "3434804602"
email_site = "https://tempemailfree.com/"

#for email api
tm_key = "e0cf276c-0a4f-47c1-9eac-f17651d42426"
tm_http = "https://api.testmail.app/api/json"
tm_ns = "g5ctz"
params = dict(
    apikey=tm_key,
    namespace=tm_ns,
    pretty="true",
    livequery="true",
    timeout=10
)
#}-------------------

#chrome options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
web = webdriver.Chrome(options=options)
stealth(web,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True
        )
#USELESS but i keep around just in case{
#doesnt work
def dd_login():
    web.get("https://identity.doordash.com/auth?client_id=1666519390426295040&intl=en-US&layout=consumer_web&prompt=none&redirect_uri=https%3A%2F%2Fwww.doordash.com%2Fpost-login%2F&response_type=code&scope=%2A&state=%2Fhome%2F%7C%7C6999544b-6d39-406e-ab3f-b616e93a3656&_gl=1*1xp33s6*_gcl_au*NjY4OTMyNjY2LjE3MjIwMzg2MjY.&_ga=2.196267308.1601632065.1722038626-404033190.1722038626")
    time.sleep(30)
    email_fld = web.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[2]/div/div/div[2]/div/div[1]/input')
    email_fld.send_keys(dd_email)
    signin_btn = web.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/button')
    signin_btn.click()
    time.sleep(2)
    try:
        pw_fld = web.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[2]/div/div/div[2]/div/div[1]/input')
        pw_fld.send_keys(dd_pw)
        signin_btn = web.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/button")
        signin_btn.click()
    except:
        time.sleep(3)
        code = dd_verify()
        f = web.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[3]/div[1]/div/div/div/div/div/input")
        f.send_keys(code[0])
        f = web.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[3]/div[2]/div/div/div/div/div/input")
        f.send_keys(code[1])
        f = web.find_element(By.XPATH,
                             "/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[3]/div[3]/div/div/div/div/div/input")
        f.send_keys(code[2])
        f = web.find_element(By.XPATH,
                             "/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[3]/div[4]/div/div/div/div/div/input")
        f.send_keys(code[3])
        f = web.find_element(By.XPATH,
                             "/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[3]/div[5]/div/div/div/div/div/input")
        f.send_keys(code[4])
        f = web.find_element(By.XPATH,
                             "/html/body/div[1]/div/div[1]/div/div/div/div/div[3]/div/div/form/div[3]/div[6]/div/div/div/div/div/input")
        f.send_keys(code[5])
    time.sleep(5)
    web.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/div[1]/div/div[1]/div[1]/div[2]/div/div[1]/header/div[2]/div[1]/div/div/a/div")
#doesnt work
def dd_verify():
    resp = requests.get(url=tm_http,params=params)
    data = resp.json()
    body = data["emails"][0]["html"]
    beautify = BeautifulSoup(body,features="html.parser")
    print(beautify)
    code = beautify.body.find('td',attrs={'class':"em_defaultlink em_font_24"}).text
    print(code)
    return code
def acc_cred_creation():
    email = ""

    web.get(email_site)
    time.sleep(3)
    try:
        email = web.find_element(By.XPATH,"/html/body/div[1]/header/div/div[3]/div/div[2]/div[2]/form/div/div[1]/div[1]/div").text
    except:
        print("fail to grab email")
        web.refresh()
        time.sleep(5)

    try:
        email = web.find_element(By.XPATH,"/html/body/div[1]/header/div/div[3]/div/div[2]/div[2]/form/div/div[1]/div[1]/div").text
    except:
        print("fail to grab email")
        web.refresh()
        time.sleep(5)
    print(email)
    web.execute_script("window.open('https://smstome.com/canada/phone/13434804602/sms/7750','secondtab');")
    web.switch_to.window("secondtab")
    time.sleep(3)
    return email
def sd_login():
    web.get("https://www.skipthedishes.com/")
    og_win = web.current_window_handle
    time.sleep(5)
    login_btn = web.find_element(By.XPATH,"/html/body/div[1]/div/div/header/div/div[2]/a[1]")
    login_btn.click()
    time.sleep(2)
    login_email_btn = web.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div/div[2]/div/button")
    login_email_btn.click()
    time.sleep(2)
    email_fld = web.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/input")
    email_fld.send_keys(sd_email)
    time.sleep(2)
    pw_fld = web.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div/div[2]/div/div[3]/div[2]/div[2]/input")
    pw_fld.send_keys(sd_pw)
    time.sleep(2)
    login_btn = web.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div/div[2]/div/div[3]/button")
    login_btn.click()
    time.sleep(5)
    try:
        web.find_element(By.XPATH,"/html/body/div[1]/div/main/div[1]/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div/input")
    except:
        print("address field input failed")
        time.sleep(2)
        try:
            verif_btn = web.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div/div/button[1]")
            verif_btn.click()
            print("phone verif clicked")
            time.sleep(10)
            web.execute_script("window.open('https://smstome.com/canada/phone/13434804602/sms/7750','secondtab');")
            web.switch_to.window("secondtab")
            mt = web.find_element(By.CLASS_NAME, "messagesTable")
            tbdy = mt.find_element(By.TAG_NAME, "tbody")
            msgs = tbdy.find_elements(By.TAG_NAME, "tr")
            code = ""
            for msg in msgs:
                comps = msg.find_elements(By.TAG_NAME, "td")
                if comps[0].text == sd_num:
                    code = comps[2].text[:5]
                    break
            if len(code) > 0:
                print(code)
                web.close()
                web.switch_to.window(og_win)
                verif_fld = web.find_element(By.XPATH, "/html/body/div[7]/div/div/div/div[1]/div/div[2]/input")
                verif_fld.send_keys(code)
            else:
                print("no code found")
                return
        except:
            print("phone verif fail")
            return
#}----

#inputs location into skip
def sd_init(adr):
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
#inputs location and item into doordash
def dd_init(adr,food):
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
    time.sleep(20)
#input location into uber eats
#may break in future? works for now tho
def ue_init(adr):
    web.get("https://www.ubereats.com/")
    time.sleep(3)
    loc_btn = web.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/main/div[1]/div[2]/div/div[1]/div/div[1]/div/div/input")
    loc_btn.send_keys(adr)
    time.sleep(3)
    adr_lst = web.find_element(By.ID,"location-typeahead-home-menu")
    adr_btn = adr_lst.find_element(By.TAG_NAME,"li")
    adr_btn.click()
    time.sleep(10)
#when calling the functions make sure to space out the address and add the city for the adr param
# sd_init("4820 201 st")
# dd_init("4820 201 st","chicken")
# ue_init("4820 201 st langley")
