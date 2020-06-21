from bs4 import BeautifulSoup
import requests
from selenium import webdriver


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
elements = driver.find_elements_by_xpath("//ytd-grid-video-renderer/div")

for el in elements:
    print(el.get_attribute("innerHTML"))
    print("\n")

# ytd-grid-video-renderer
# [contains(text(),'Videos')]
# /html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/app-toolbar/div/div/paper-tabs/div/div/paper-tab[2]/div