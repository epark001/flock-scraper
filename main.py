import os
import sys
import jwt
import json
import time
import sched
from google.cloud import bigquery
from google.oauth2 import service_account

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from datetime import datetime, timezone
import requests
from pytz import reference
from dateutil import tz
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# for local
# path = './chromedriver/mac/chromedriver'
# for server
path = '/home/edward_vadepark_com/flock-scraper/chromedriver/lin/chromedriver'
# path = './chromedriver'
os.chmod(path, 755)

s = sched.scheduler(time.time, time.sleep)
# interval in seconds
loopInterval = 1 * 60

oauth = None
oauth_expire = 0

# local
credentials = service_account.Credentials.from_service_account_file(
    'secrets/vade-backend-509b193ba372.json', scopes=["https://www.googleapis.com/auth/cloud-platform"])
client = bigquery.Client(credentials=credentials, project='vade-backend')

# gcp
# client = bigquery.Client()


last_timestamp = ''
with open('last_timestamp.txt', 'r') as file:
    last_timestamp = file.read()

with open('secrets/flock-login.json', 'r') as file:
    data = file.read()

# parse file
flock_login = json.loads(data)

ser = Service(path)

# chrome headless mode for server
WINDOW_SIZE = "1920,1080"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')


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

        # for mac
        # driver = webdriver.Chrome(options=chrome_options)

        # for server
        driver = webdriver.Chrome(
            path, options=chrome_options)

        driver.maximize_window()
        driver.get(url)
        # wait 10 seconds if page/element does not load
        driver.implicitly_wait(10)

        driver.find_element(By.NAME, "email").send_keys(
            flock_login['username'])
        driver.find_element(By.NAME, "password").send_keys(
            flock_login['password'])

        driver.find_element(By.NAME, "submit").click()
        time.sleep(10)
        global oauth

        for request in driver.requests:
            if request.response:
                if 'https://margarita.flocksafety.com/' in request.url:
                    oauth = request.headers['Authorization']

        driver.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)


def check_oauth():
    if oauth is None or oauth_expire < datetime.datetime.now().timestamp():
        refresh_oath_jwt()
        oauth_expire = jwt.decode(oauth.split('Bearer ')[1], options={
                                  "verify_signature": False})['exp']
    return


def parse_results(results):
    if len(results) < 1:
        return []
    global last_timestamp
    output = []
    for result in results:
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
        plate = Point(plate_center)
        spot = Polygon([[274, 255], [634, 158], [1917, 560], [
                        1919, 1078], [1499, 1078]])
        if spot.contains(plate) is True:
            output.append({
                'time': result['object']['capturedAt'][:-5],
                'plate': ocr,
                'spot_uuid': '5ebf711d-db50-4a82-8066-2d6a6ee44e10',
                'plate_center': json.dumps(plate_center),
                'plate_bounds': json.dumps(plate_bounds),
                'car_bounds': json.dumps(car_bounds),
                'car_center': json.dumps(car_center),
                'raw_data': json.dumps(result),
                'within_bounds': True
            })
        last_timestamp = result['object']['capturedAt']
    print("within_bounds: ", len(output))
    table_id = "vade-backend.beta_plates.reading_plates"

    errors = client.insert_rows_json(table_id, output)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
    return output


def scrape_flock():
    global last_timestamp
    check_oauth()
    url = "https://margarita.flocksafety.com/api/v1/search"
    headers = {
        "Authorization": oauth
    }
    post_json = {
        "cameraExternalIds": ["2ad49b27-24b3-46a3-9f5c-3ea929c546a5"],
        "corpus": "onlyPlates",
        "dateFilter": {
            "ranges": [
                {
                    # "start": "2022-02-04T19:53:00.000-05:00",
                  "start": last_timestamp,
                  "end": datetime.now(timezone.utc).isoformat()
                    #   "end":   "2022-02-22T21:53:00.000-05:00"
                }
            ],
            "operator": "or"
        },
        "licensePlates": {},
        "residency": "Any",
        "reason": "RPA study",
        "pageSize": 500,
        "order": "asc"
    }
    output = []
    response = requests.post(url, headers=headers, json=post_json)
    resp = response.json()
    print("total results: ", resp['totalResults'])
    while resp['totalResults'] > 1:
        print("------------")
        print("results: ", len(resp['results']))
        output.extend(parse_results(resp['results']))

        post_json['dateFilter']['ranges'][0]['start'] = last_timestamp
        print(post_json['dateFilter']['ranges'][0])
        response = requests.post(url, headers=headers,
                                 json=post_json, timeout=30)
        resp = response.json()
    with open('last_timestamp.txt', 'w') as f:
        f.write(last_timestamp)
    print("============")
    print(len(output))


def startup():
    now = datetime.now()
    localtime = reference.LocalTimezone()
    print("------------------------------------------")
    print("start up")
    print(time.strftime("%a, %D %H:%M:%S", time.localtime()), localtime.tzname(now))
    print("------------------------------------------")


# server
startup()
# scrape_flock()
s.enter(loopInterval, 0, scrape_flock, ())
s.run()
