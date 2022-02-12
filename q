[1mdiff --git a/README.md b/README.md[m
[1mindex e0354e4..a477b2f 100644[m
[1m--- a/README.md[m
[1m+++ b/README.md[m
[36m@@ -3,4 +3,9 @@[m
 Install pillow for some isntances if PIL does not import[m
 ```[m
 pip install pillow[m
[32m+[m[32mpip install selenium[m
 ```[m
[32m+[m[32msudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add[m
[32m+[m[32msudo echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list[m
[32m+[m[32msudo apt-get -y update[m
[32m+[m[32msudo apt-get -y install google-chrome-stable[m
\ No newline at end of file[m
[1mdiff --git a/aspen_current.png b/aspen_current.png[m
[1mindex 6310aae..61710de 100644[m
Binary files a/aspen_current.png and b/aspen_current.png differ
[1mdiff --git a/main.py b/main.py[m
[1mindex 30d15c1..3888f7d 100644[m
[1m--- a/main.py[m
[1m+++ b/main.py[m
[36m@@ -9,10 +9,10 @@[m [mfrom selenium import webdriver[m
 from selenium.webdriver.chrome.options import Options[m
 [m
 # for local[m
[31m-# path = './'[m
[32m+[m[32mpath = './'[m
 #for server[m
[31m-path = '/home/edward_vadepark_com/aspen-scraper'[m
[31m-os.chmod(path+'/chromedriver_linux64/chromedriver', 755)[m
[32m+[m[32m# path = '/home/edward_vadepark_com/aspen-scraper'[m
[32m+[m[32m# os.chmod(path+'/chromedriver_linux64/chromedriver', 755)[m
 [m
 s = sched.scheduler(time.time, time.sleep)[m
 # interval in seconds[m
[36m@@ -35,18 +35,19 @@[m [mdef scrape_aspen_livestream():[m
         url = "https://c.streamhoster.com/embed/media/O7sB36/6WW26anes7e/KmYuWfscTlW_5"[m
 [m
         #for local[m
[31m-        # driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe')[m
[32m+[m[32m        driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe')[m
         # driver = webdriver.Chrome('C:/Users/sseie/1_Directory/Vade/chromedriver/chromedriver.exe', options=chrome_options)[m
 [m
         #for server[m
[31m-        driver = webdriver.Chrome(path+'/chromedriver_linux64/chromedriver', options=chrome_options)[m
[32m+[m[32m        # driver = webdriver.Chrome(path+'/chromedriver_linux64/chromedriver', options=chrome_options)[m
 [m
         driver.maximize_window()[m
         driver.get(url)[m
         # wait 10 seconds if page/element does not load[m
         driver.implicitly_wait(10)[m
 [m
[31m-        driver.find_elements_by_css_selector("[class*='vjs-big-play-button']")[0].click()[m
[32m+[m[32m        driver.find_element_by_css_selector("[class*='vjs-big-play-button']")[0].click()[m
[32m+[m[32m        # driver.find_element_by_xpath('//*[@id="playerEl"]/button').click()[m
         time.sleep(5)[m
         driver.save_screenshot('aspen_current.png')[m
 [m
[36m@@ -60,7 +61,7 @@[m [mdef scrape_aspen_livestream():[m
         files = [('file', image_file)][m
         upload_status = requests.post(ingest, headers=header, data=payload, files=files)[m
         print(upload_status)[m
[31m-        files.close()[m
[32m+[m[32m        image_file.close()[m
 [m
         driver.close()[m
     except Exception as e:[m
[36m@@ -81,5 +82,6 @@[m [mdef startup():[m
 [m
 #server[m
 startup()[m
[32m+[m[32m# scrape_aspen_livestream()[m
 s.enter(loopInterval, 0, scrape_aspen_livestream, ())[m
 s.run()[m
\ No newline at end of file[m
