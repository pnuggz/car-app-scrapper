from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import mysql.connector
import time
import datetime

from pyvirtualdisplay import Display
display = Display(visible=0, size=(1920, 1080))
display.start()

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-setuid-sandbox")
driver = webdriver.Chrome(chrome_options=chrome_options)

con = mysql.connector.connect(user='carsales_user',password='Jatipadang13',host='103.253.146.240',database='api',port='3306')

cursor = con.cursor()

sql_user_searches = "SELECT user_id, make_id, make_name, model_id, model_name, location_id, location, location_link, last_update FROM `carsales_users_search` JOIN carsales_makes ON carsales_makes.id = carsales_users_search.make_id JOIN carsales_models ON carsales_models.id = carsales_users_search.model_id JOIN carsales_locations ON carsales_locations.id = carsales_users_search.location_id WHERE carsales_users_search.status = 0"
cursor.execute(sql_user_searches)
searches = cursor.fetchall()

for z in searches:
    print(z[8])
    print(datetime)
    offset = 0
    url = "https://www.carsales.com.au/cars/{0}/{1}/{2}".format(z[2],z[4],z[7])
    sleep_time = 5
    num_retries = 100
    error = 0
    for loopingcow in range(0, num_retries):  
        try:
            error = 0
            driver.get(url)
            time.sleep(sleep_time)
            driver.find_element_by_xpath("""//*[@class="result-set-container "]""").get_attribute("outerHTML")
            print("success")
        except NoSuchElementException:
            print("error")
            error = 1
            pass

        if error == 1:
            time.sleep(sleep_time)  # wait before trying to fetch the data again
            sleep_time += 1  # Implement your backoff algorithm here i.e. exponential backoff
        else:
            break
    total_pagination = driver.find_elements_by_xpath("""//div[@class="tabbed-pagination"]/div[@class="pagination-container"]/div[@class="pagination-container"]/div[@class="pagination"]/p""")[0].text
    number_of_pages_split = total_pagination.split(" ")
    number_of_pages = int(number_of_pages_split[1])
    page = 0
    while page < number_of_pages:
        offset = page * 12
        url = "https://www.carsales.com.au/cars/{0}/{1}/{2}?offset={3}".format(z[2],z[4],z[7],offset)
        print(url)
        sleep_time = 5
        num_retries = 100
        error = 0
        for loopyloop in range(0, num_retries):  
            try:
                error = 0
                driver.get(url)
                time.sleep(sleep_time)
                driver.find_element_by_xpath("""//*[@class="result-set-container "]""").get_attribute("outerHTML")
                print("success")
            except NoSuchElementException:
                print("error")
                error = 1
                pass

            if error == 1:
                time.sleep(sleep_time)  # wait before trying to fetch the data again
                sleep_time += 1  # Implement your backoff algorithm here i.e. exponential backoff
            else:
                break
        try:
            rows = driver.find_elements_by_xpath("""//div[contains(@class,"result-set-container ")]/div[contains(@class,"listing-item")]""")
            count = len(rows)
            i = 0
            while i < count:        
                value = ""

                try:
                    value_good = rows[i].find_elements_by_xpath("""//a[contains(@class,"badge-good-price")]""")[i].get_attribute("class")
                except:
                    value_good = ""
                try:
                    value_great = rows[i].find_elements_by_xpath("""//a[contains(@class,"badge-great-price")]""")[i].get_attribute("class")
                except:
                    value_great = ""
                
                if value_good != "":
                    value = "Good Price"
                if value_great != "":
                    value = "Great Price"
                
                print(value)
                if value != "":
                    title = rows[i].find_elements_by_xpath("""//div[contains(@class,"title ")]/a/h2""")[i].text
                    odometer_raw = rows[i].find_elements_by_xpath("""//div[contains(@class,"listing-body")]/div[contains(@class,"ad-info")]/div[contains(@class,"ad-features")]/div[contains(@class,"vehicle-features")]/div[contains(@class,"listing-feature")][1]/div[contains(@class,"feature-text")]""")[i].text
                    body = rows[i].find_elements_by_xpath("""//div[contains(@class,"listing-body")]/div[contains(@class,"ad-info")]/div[contains(@class,"ad-features")]/div[contains(@class,"vehicle-features")]/div[contains(@class,"listing-feature")][2]/div[contains(@class,"feature-text")]""")[i].text
                    transmission = rows[i].find_elements_by_xpath("""//div[contains(@class,"listing-body")]/div[contains(@class,"ad-info")]/div[contains(@class,"ad-features")]/div[contains(@class,"vehicle-features")]/div[contains(@class,"listing-feature")][3]/div[contains(@class,"feature-text")]""")[i].text
                    engine = rows[i].find_elements_by_xpath("""//div[contains(@class,"listing-body")]/div[contains(@class,"ad-info")]/div[contains(@class,"ad-features")]/div[contains(@class,"vehicle-features")]/div[contains(@class,"listing-feature")][4]/div[contains(@class,"feature-text")]""")[i].text
                    price_raw = rows[i].find_elements_by_xpath("""//div[contains(@class,"ad-price")]/a/div[@class="price"][1]""")[i].text
                    link_raw = rows[i].find_elements_by_xpath("""//div[contains(@class,"location-info")]/div[contains(@class,"action-buttons")]/a""")[i].get_attribute("href")
                    year_raw = title[:4]
                    try:
                        year = int(year_raw)
                    except:
                        year = ""
                    odometer_replace = odometer_raw.replace(" km","").replace(",","")
                    try:
                        odometer = int(odometer_replace)
                    except:
                        odometer = ""
                    price_replace = price_raw.replace("$","").replace(",","").replace("*","")
                    try:
                        price = int(price_replace)
                    except:
                        price = ""
                    link_split = link_raw.split("?")
                    link = link_split[0]
                    i = i + 1
                    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                    query = """INSERT INTO carsales_results_raw (source, make_id, model_id, year, odometer, body, transmission, engine, price, value, link) VALUES ('Carsales', '{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}') ON DUPLICATE KEY UPDATE price = '{7}', last_update = '{10}' """.format(z[1], z[3], year, odometer, body, transmission, engine, price, value, link, timestamp)
                    cursor.execute(query)
                    con.commit()
                else:
                    print("No Good")
                    i = i + 1
            page = page + 1
        except NoSuchElementException:
            pass

cursor.close()
con.close()
driver.quit()
display.popen.kill()
print("success")