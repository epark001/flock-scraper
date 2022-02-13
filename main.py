import os
import sys
import jwt
import time
import sched
from google.cloud import bigquery

from datetime import datetime
import requests
from pytz import reference
from dateutil import tz
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# for local
# path = './chromedriver/mac/chromedriver'
# for server
# path = '/home/edward_vadepark_com/aspen-scraper'
path = '.'
os.chmod(path+'/lin/chromedriver', 755)

s = sched.scheduler(time.time, time.sleep)
# interval in seconds
loopInterval = 1 * 60

oauth = None
oauth_expire = 0
client = bigquery.Client()


# from selenium import webdriver
# ser = Service("C:\\chromedriver.exe")
ser = Service(path)
# op = webdriver.ChromeOptions()
# s = webdriver.Chrome(service=ser, options=op)

# chrome headless mode for server
WINDOW_SIZE = "1920,1080"
chrome_options = webdriver.ChromeOptions()
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
# chrome_options.add_argument('--no-sandbox')


def refresh_oath_jwt():
    try:

        t = time.localtime()
        current_time = time.strftime("%D %H:%M:%S", t)
        print("============")
        print("time: ")
        print(current_time)
        url = "https://search.flocksafety.com"

        # for local
        # driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe')
        # driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe', options=chrome_options)

        # driver = webdriver.Chrome(service=Service)
        driver = webdriver.Chrome(options=chrome_options)

        # for server
        # driver = webdriver.Chrome(
        # path+'/chromedriver_linux64/chromedriver', options=chrome_options)

        driver.maximize_window()
        driver.get(url)
        # wait 10 seconds if page/element does not load
        driver.implicitly_wait(10)

        driver.find_element(By.NAME, "email").send_keys(
            'test')
        driver.find_element(By.NAME, "password").send_keys('test')

        # driver.find_element_by_css_selector("[class*='vjs-big-play-button']")[0].click()
        driver.find_element(By.NAME, "submit").click()
        time.sleep(10)
        global oauth    # Needed to modify global copy of globvar

        for request in driver.requests:
            if request.response:
                if 'https://margarita.flocksafety.com/' in request.url:
                    # if oauth == request.headers['Authorization']:
                    #     print("same")
                    # else:
                    #     print("diff")
                    #     print(request.headers['Authorization'])
                    oauth = request.headers['Authorization']

                    # print(
                    # request.url,
                    # request,
                    # request.headers['Authorization'],
                    # request.response.status_code,
                    # request.response.headers,
                    # '\n--------------------------------'
                    # )

        # print(driver.get_cookies())
        # driver.save_screenshot('aspen_current.png')

        # ingest = "https://us-central1-vade-backend.cloudfunctions.net/vade_ingest_bandaid"
        # header = {"apiKey": "abc123"}
        # payload = {
        #     "cameraID": '6c7b36e8-2b58-48e0-b4f6-ae56c1d59037',
        #     "apiKey": "abc123"
        # }
        # image_file = open('aspen_current.png', 'rb')
        # files = [('file', image_file)]
        # upload_status = requests.post(
        #     ingest, headers=header, data=payload, files=files)
        # print(upload_status)
        # image_file.close()

        driver.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
    # s.enter(loopInterval, 1, scrape_aspen_livestream, ())


def check_oauth():
    if oauth is None or oauth_expire < datetime.datetime.now().timestamp():
        refresh_oath_jwt()
        oauth_expire = jwt.decode(oauth.split('Bearer ')[1], options={
                                  "verify_signature": False})['exp']
    return


def test_flock_oauth():
    check_oauth()
    url = "https://margarita.flocksafety.com/api/v1/search"
    apiKey = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJEY3pOVVpCT0VSQlFVWTRSREkyUmpNd09EazNORVUwTTBORFJqbENRamRDTlRNek5UTkNOZyJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLmZsb2Nrc2FmZXR5LmNvbS8iLCJzdWIiOiJhdXRoMHw2MGQ2MDkyYTQyOGI1ZDAwNmFlZjc3Y2MiLCJhdWQiOlsiY29tLmZsb2Nrc2FmZXR5Lm1hcmdhcml0YS5wcm9kIiwiaHR0cHM6Ly9wcm9kLWZsb2NrLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2NDM1OTc1OTQsImV4cCI6MTY0MzY4Mzk5NCwiYXpwIjoiMDZOZnJ1NnhScXpWUEFsam85N1h4SzdGZWRvUjdJRVkiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIn0.UvJCJU08O_OK8tGFh-jGe3FKCH0hRaHn9JWUYl2uu3qzkN2GJbFPg_gJ8iJeS6HOHENDDz4CYYhNAOSnH0cSQ9kjfpEBdfIhxTNI1Ous4N0ZM5ZSFpnQMdfzvPz5wITxRVer7NzcUWV-KP953aLq1FbaXKTmtvVwiRFTw1UA4339yTFrRqoKIRcGQzqlFFmtffiK_oCZdYwpmHk7plW0Tf71_ZTTROjtsI2ZUDhO4v4gNLQZw2yhQvFL1tf9dTQY2sGODL-DDDGL6SM8UAABw0W-2c3qSwr0--ZNbcrPyZxFx4NDl6KKlR2Yxf3zuDG2sRrTCPzON4x6lMNvDWPYEg"
    headers = {
        "Authorization": oauth
    }
    post_json = {
        "cameraExternalIds": ["2ad49b27-24b3-46a3-9f5c-3ea929c546a5"],
        "corpus": "onlyPlates",
        "dateFilter": {
            "ranges": [
                {"start": "2022-02-04T19:53:00.000-05:00",
                  "end": "2022-02-05T21:53:00.000-05:00"
                 }
            ],
            "operator": "or"
        },
        "licensePlates": {},
        "residency": "Any",
        "reason": "RPA study",
        "pageSize": 100,
        "order": "desc"
    }
    output = []
    response = requests.post(url, headers=headers, json=post_json)
    resp = response.json()
    print("total results: ", resp['totalResults'])
    if 'nextPageId' in resp:
        while 'nextPageId' in resp:
            print("------------")
            print("next page: ", resp['nextPageId'])
            print("count: ", len(resp['results']))
            for result in resp['results']:
                ocr = None
                plate_bounds = []
                plate_center = []
                car_bounds = []
                car_center = []
                for attr in result['object']['attributes']:
                    if attr['class'] == 'ocr':
                        ocr = attr['value']
                        bb = attr['bestBox']
                        plate_bounds.append([bb['x'], bb['y']])
                        plate_bounds.append([bb['x']+bb['width'], bb['y']])
                        plate_bounds.append(
                            [bb['x']+bb['width'], bb['y']+bb['height']])
                        plate_bounds.append([bb['x'], bb['y']+bb['height']])
                        plate_center = [
                            bb['x'] + (bb['width']/2), bb['y'] + (bb['height']/2)]
                    if attr['class'] == 'vehicle_type':
                        bb = attr['bestBox']
                        car_bounds.append([bb['x'], bb['y']])
                        car_bounds.append([bb['x']+bb['width'], bb['y']])
                        car_bounds.append(
                            [bb['x']+bb['width'], bb['y']+bb['height']])
                        car_bounds.append([bb['x'], bb['y']+bb['height']])
                        car_center = [
                            bb['x'] + (bb['width']/2), bb['y'] + (bb['height']/2)]
                output.append({
                    'time': result['object']['capturedAt'],
                    'plate': ocr,
                    'spot_uuid': '5ebf711d-db50-4a82-8066-2d6a6ee44e10',
                    'plate_center': plate_center,
                    'plate_bounds': plate_bounds,
                    'car_bounds': car_bounds,
                    'car_center': car_center,
                    'raw_data': result
                })
            resp = requests.get(
                url+'/page/'+resp['nextPageId'], headers=headers).json()
        print("------------")
        print("last page")
        print("count: ", len(resp['results']))
        for result in resp['results']:
            ocr = None
            plate_bounds = []
            plate_center = []
            car_bounds = []
            car_center = []
            for attr in result['object']['attributes']:
                if attr['class'] == 'ocr':
                    ocr = attr['value']
                    bb = attr['bestBox']
                    plate_bounds.append([bb['x'], bb['y']])
                    plate_bounds.append([bb['x']+bb['width'], bb['y']])
                    plate_bounds.append(
                        [bb['x']+bb['width'], bb['y']+bb['height']])
                    plate_bounds.append([bb['x'], bb['y']+bb['height']])
                    plate_center = [
                        bb['x'] + (bb['width']/2), bb['y'] + (bb['height']/2)]
                if attr['class'] == 'vehicle_type':
                    bb = attr['bestBox']
                    car_bounds.append([bb['x'], bb['y']])
                    car_bounds.append([bb['x']+bb['width'], bb['y']])
                    car_bounds.append(
                        [bb['x']+bb['width'], bb['y']+bb['height']])
                    car_bounds.append([bb['x'], bb['y']+bb['height']])
                    car_center = [
                        bb['x'] + (bb['width']/2), bb['y'] + (bb['height']/2)]
            output.append({
                'time': result['object']['capturedAt'],
                'plate': ocr,
                'spot_uuid': '5ebf711d-db50-4a82-8066-2d6a6ee44e10',
                'plate_center': plate_center,
                'plate_bounds': plate_bounds,
                'car_bounds': car_bounds,
                'car_center': car_center,
                'raw_data': result
            })
        # print(resp)
    print("============")
    print(len(output))
    # print(output[0])

    # Construct a BigQuery client object.

    # TODO(developer): Set table_id to the ID of table to append to.
    table_id = "vade-backend.beta_plates.reading_plates"

    # Make an API request.
    errors = client.insert_rows_json(table_id, output)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))

    # print(resp.text)
    # results = resp.json()
    # print("results: ", len(results['results']))
    # print("total results: ", results['totalResults'])
    # print("next page id: ", results['nextPageId'])


def startup():
    now = datetime.now()
    localtime = reference.LocalTimezone()
    print("------------------------------------------")
    print("start up")
    print(time.strftime("%a, %D %H:%M:%S", time.localtime()), localtime.tzname(now))
    print("------------------------------------------")

# testing
# scrape_aspen_livestream()


# server
# startup()
test_flock_oauth()
# s.enter(loopInterval, 0, scrape_aspen_livestream, ())
# s.run()
