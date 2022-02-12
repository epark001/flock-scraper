import os
import time
import sched
from datetime import datetime
import requests
from pytz import reference
from dateutil import tz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# for local
# path = './'
#for server
path = '/home/edward_vadepark_com/aspen-scraper'
os.chmod(path+'/chromedriver_linux64/chromedriver', 755)

s = sched.scheduler(time.time, time.sleep)
# interval in seconds
loopInterval = 1 * 60

# chrome headless mode for server
WINDOW_SIZE = "1920,1080"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')
    
def scrape_aspen_livestream():
    try:
        t = time.localtime()
        current_time = time.strftime("%D %H:%M:%S", t)
        print("============")
        print("time: ")
        print(current_time)
        url = "https://c.streamhoster.com/embed/media/O7sB36/6WW26anes7e/KmYuWfscTlW_5"

        #for local
        # driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe')
        # driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe', options=chrome_options)

        #for server
        driver = webdriver.Chrome(path+'/chromedriver_linux64/chromedriver', options=chrome_options)

        driver.maximize_window()
        driver.get(url)
        # wait 10 seconds if page/element does not load
        driver.implicitly_wait(10)

        # driver.find_element_by_css_selector("[class*='vjs-big-play-button']")[0].click()
        driver.find_element_by_xpath('//*[@id="playerEl"]/button').click()
        time.sleep(5)
        driver.save_screenshot('aspen_current.png')

        ingest = "https://us-central1-vade-backend.cloudfunctions.net/vade_ingest_bandaid"
        header = {"apiKey": "abc123"}
        payload = {
            "cameraID": '6c7b36e8-2b58-48e0-b4f6-ae56c1d59037',
            "apiKey": "abc123"
        }
        image_file = open('aspen_current.png', 'rb')
        files = [('file', image_file)]
        upload_status = requests.post(ingest, headers=header, data=payload, files=files)
        print(upload_status)
        image_file.close()

        driver.close()
    except Exception as e:
            print(e)
    s.enter(loopInterval, 1, scrape_aspen_livestream, ())

def startup():
    now = datetime.now()
    localtime = reference.LocalTimezone()
    print("------------------------------------------")
    print("start up")
    print(time.strftime("%a, %D %H:%M:%S", time.localtime()), localtime.tzname(now))
    print("------------------------------------------")

#testing
# scrape_aspen_livestream()


#server
startup()
# scrape_aspen_livestream()
s.enter(loopInterval, 0, scrape_aspen_livestream, ())
s.run()