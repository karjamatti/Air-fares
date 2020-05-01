'''
Created on Feb 28, 2019

@author: Matti

This script is for Scraping air fare data from the ITA-matrix airfare search.
The script runs a Gooogle chrome webdriver, which should be installed in the correct directory.

Sleep times should be adjusted based on circumstances to ensure functionality of script
'''
import time
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""
URL INFO
---
This part defines the URL to be scraped, webdriver to be used as well as title keyword for authentication
"""
page_url = 'https://matrix.itasoftware.com/'
kwrd = 'ITA'
driver = webdriver.Chrome()
driver.get(page_url)
assert kwrd in driver.title # makes sure the url is correct

"""
ELEMENT XPATHS
---
This part defines the Xpaths of the desired elements
"""
ac_click = ".//*[contains(text(), 'Advanced controls')]" # Opens the 'Advanced controls' -fields
out_car = '//*[@id="searchPanel-0"]/div/table/tbody/tr[2]/td/div/div[1]/div/div/div[3]/div/div[2]/input[1]' # Outbound carrier field
ret_car = '//*[@id="searchPanel-0"]/div/table/tbody/tr[2]/td/div/div[1]/div/div/div[5]/div/div[2]/input[1]' # Return carrier field
orig_elem = '//*[@id="cityPair-orig-0"]' # Origin field
dest_elem = '//*[@id="cityPair-dest-0"]' # Destination field
lf_click = '//*[@id="gwt-uid-168"]' # Opens the low fare calendar
start_elem = '//*[@id="calDate-0"]' # Calendar start field
sl_elem = '//*[@id="calStay-0"]' # Stay length field
cabin_elem = '//*[@id="searchPanel-0"]/div/div/div[4]/div/select' # Cabin drop down list
searchbox_elem = '//*[@id="searchButton-0"]' # Search box element

"""
ELEMENT CLASSES
---
This part defines the classes for objects passed onto BeautifulSoup's find_all -method.
"""
pricetag_cls = 'IR6M2QD-c-c' # Price-date combos on the search result page should be of this class
datetag_cls = 'IR6M2QD-c-d' # Departure dates on the search result page should be of this class

"""
JAVASCRIPT COMMANDS
---
This part defines the javaScript -commands used by the webdriver
"""
click_element = "arguments[0].click();" # Webdriver clicks on element

"""
PREFERENCES
---
This part lists the search parameters and preferences of the user
"""
today = str(dt.today().strftime('%m/%d/%Y'))
carrier_str_list = ['AY+']
carrier_str = 'AY+'
orig_str_list = ['ARN', 'PRG', 'RIX', 'BUD']
orig_str = 'HEL'
dest_str_list = ['DEL', 'BKK', 'SIN', 'JFK', 'ORD']
dest_str = 'ARN'
start_str = today
stay_length_list = [1,2,3,4,5,6,7]
stay_length = 1
cabin_str = 'Business class or higher'
maxwait = 60 # Max wait for search to return prices

"""
SCRIPT
---
Below you'll find the actual script for scraping the prices. Happy Scraping!
"""

def start_over():
    driver.get(page_url)    

# Make Advanced controls visible
def adv_ctrl():
    click_str = driver.find_element_by_xpath(ac_click)
    driver.execute_script(click_element, click_str)
    time.sleep(1)

# Set carrier
def set_carrier(carrier_str):
    out_carrier = driver.find_element_by_xpath(out_car)
    out_carrier.clear()
    out_carrier.send_keys(carrier_str)
    ret_carrier = driver.find_element_by_xpath(ret_car)
    ret_carrier.clear()
    ret_carrier.send_keys(carrier_str)

# Set Origin
def set_origin(orig_str):
    origin = driver.find_element_by_xpath(orig_elem)
    origin.clear()
    origin.send_keys(orig_str)

# Set destination
def set_destination(dest_str):
    destination = driver.find_element_by_xpath(dest_elem)
    destination.clear()
    destination.send_keys(dest_str)
    destination.send_keys(Keys.RETURN)

# Select low-fare calendar
def low_fare():
    clickbox = driver.find_element_by_xpath(lf_click)
    driver.execute_script(click_element, clickbox)
    time.sleep(1)

# Set date
def set_date(start_str):
    start = driver.find_element_by_xpath(start_elem)
    start.clear()
    start.send_keys(start_str)
    start.send_keys(Keys.RETURN)

# Set lenght of stay
def set_length(stay_length):
    sl_str = str(stay_length)
    sl = driver.find_element_by_xpath(sl_elem)
    sl.clear()
    sl.send_keys(sl_str)

# Choose cabin
def choose_cabin():
    select = Select(driver.find_element_by_xpath(cabin_elem))
    select.select_by_visible_text(cabin_str)

# SEARCH
def search():
    searchbox = driver.find_element_by_xpath(searchbox_elem)
    driver.execute_script(click_element, searchbox)
    time.sleep(1)
    
def get_new_page():
    driver.current_window_handle
    checker = True
    try:
        WebDriverWait(driver, maxwait).until(
        EC.presence_of_element_located((By.CLASS_NAME, pricetag_cls)))
    except TimeoutException:
        checker = False
    return checker
    
def get_pricetags(soup, checker):
    if not checker:
        combotags, datetags = [], []
    else:
        combotags = soup.find_all(class_ = pricetag_cls)
        datetags = soup.find_all(class_ = datetag_cls)
    return combotags, datetags

def get_prices(combotags, datetags):
    combos = [combo.text for combo in combotags]
    dates = [date.text for date in datetags]
    prices = [combo.replace(date, '', 1) for combo, date in zip(combos, dates)]
    combos = list(zip(dates, prices))
    return combos

def write_results(combos, carrier_str, orig_str, dest_str, stay_length):
    output = open("scrapings.txt", "a", encoding = "utf-8")
    month_chk = 0
    for combo in combos:
        change_year = False
        month_chk += 1
        if combo[1] != '' and combo[1] != ' ':
            if month_chk > int(combo[0]) and int(dt.today().strftime('%m')) != 12:
                month = str(int(dt.today().strftime('%m')) + 1)
            elif month_chk > int(combo[0]):
                change_year = True
                month = str(1)
            else:
                month = str(dt.today().strftime('%m'))
            if change_year:
                year = str(int(dt.today().strftime('%Y')) + 1)
            else:
                year = str(dt.today().strftime('%Y'))
            output.write(carrier_str + " " + 
                         orig_str + " " + 
                         dest_str + " " + 
                         combo[0] + "/" + month + "/" + year + " " + 
                         str(stay_length) + " "  + 
                         combo[1] + " " + 
                         str(dt.now()) + "\n")
    output.close()  

def main():
    for carrier_str in carrier_str_list:
        for orig_str in orig_str_list:
            for dest_str in dest_str_list:
                for stay_length in stay_length_list:
                    start_over()
                    adv_ctrl()
                    set_carrier(carrier_str)
                    set_origin(orig_str)
                    set_destination(dest_str)
                    low_fare()
                    set_date(start_str)
                    set_length(stay_length)
                    choose_cabin()
                    search()
                    time.sleep(1)
                    checker = get_new_page()
                    html = driver.page_source
                    soup = bs(html, features="lxml")
                    combotags, datetags = get_pricetags(soup, checker)
                    combos = get_prices(combotags, datetags)
                    write_results(combos, carrier_str, orig_str, dest_str, stay_length)
      
main()