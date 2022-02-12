import base64
import sched
from io import BytesIO
from PIL import Image
from vade_crud_api_src.vade_crud_api import *

s = sched.scheduler(time.time, time.sleep)
lastImage = None
saveImage = False
# interval in seconds
loopInterval = 5 * 60
url = 'https://www.coloradowebcam.net/webcam/aspensq03/current.jpg'
ingestUrl = 'https://ingest.beta.inf.vadenet.org/v1/upload'

print("------------------------------------------")
print("start up")
print(time.strftime("%D %H:%M:%S", time.localtime()))
print("------------------------------------------")

def grab_aspen_feed(latestImage):
    try:
        t = time.localtime()
        current_time = time.strftime("%D %H:%M:%S", t)
        print("time: ")
        print(current_time)
        response = requests.get(url, stream=True)
        latestImage = base64.b64encode(response.content)
        im = Image.open(BytesIO(base64.b64decode(latestImage)))
        im.save('aspen_last_image.jpg', 'JPEG')
        crud = VadeCrudApi("abc123", ProductionLevel.BETA)
        camera = crud.camera_crud.get_camera_by_uuid("6c7b36e8-2b58-48e0-b4f6-ae56c1d59037")
        print(camera)
        curr_time = int(time.time())
        successful_upload = crud.ingest.ingest_post_camera(camera, open('aspen_last_image.jpg', 'rb'), time_taken=curr_time)
        print(successful_upload)
        if successful_upload:
            print("uploaded image!")
        s.enter(loopInterval, 1, grab_aspen_feed, (latestImage,))
    except ValueError:
        print("error: " + ValueError)


s.enter(loopInterval, 1, grab_aspen_feed, (lastImage,))
s.run()

# manual test
# grab_aspen_feed(lastImage)
