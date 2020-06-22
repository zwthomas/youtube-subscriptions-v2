from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time


driver = webdriver.Firefox() 
channel = "https://www.youtube.com/channel/"
linus = "UCXuqSBlHAE6Xw-yeJA0Tunw"
driver.get(channel + linus)
elements = driver.find_elements_by_xpath("//paper-tab/div")
# element.click()
for el in elements:
    if "Videos" in el.get_attribute("innerHTML"):
        el.click()
        break
time.sleep(3)
elements = driver.find_elements_by_xpath("//ytd-grid-video-renderer/div")

# anchor = elements[0].find_elements_by_tag_name("a")
# videoId = anchor[0].get_attribute("href")

for el in elements:
    anchors = el.find_elements_by_tag_name("a")
    if len(anchors) == 0: continue
    videoId = anchors[0].get_attribute("href").split("=")[-1]
    print(videoId)
    # print(el.get_attribute("innerHTML"))
    # print("\n")

# ytd-grid-video-renderer
# [contains(text(),'Videos')]
# /html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/app-toolbar/div/div/paper-tabs/div/div/paper-tab[2]/div