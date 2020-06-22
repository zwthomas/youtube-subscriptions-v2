from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import time
import sqlite3

class Youtube:
    
    def getChannelAndMostRecent(self):
        conn = sqlite3.connect("./youtube.db")
        c = conn.cursor()
        c.execute("SELECT channelId, mostRecentId FROM subs")

        subInfo = {sub[0]: sub[1] for sub in c.fetchall()}

        conn.commit()
        conn.close()

        return subInfo

    def getNewVideosForSub(self, driver, channelId, recentVideo):

        channel = "https://www.youtube.com/channel/"
        driver.get(channel + channelId)

        # Nav to video tab
        elements = driver.find_elements_by_xpath("//paper-tab/div")
        for el in elements:
            if "Videos" in el.get_attribute("innerHTML"):
                el.click()
                break

        # Wait for videos to load
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.TAG_NAME, "ytd-channel-sub-menu-renderer")))

        # Get all the uploaded videos. Iterate through them until we find the previous most recent vide
        newVideos = []
        elements = driver.find_elements_by_xpath("//ytd-grid-video-renderer/div")
        for el in elements:
            try:
                anchors = el.find_elements_by_tag_name("a")
            except:
                print(el)

            if len(anchors) == 0: continue

            videoId = anchors[0].get_attribute("href").split("=")[-1]
            
            if recentVideo == videoId:
                return newVideos
            
            newVideos.append(videoId)
           

    def postInDiscord(self, newVideos, channelId):
        # Do stuff
        return

    def updateMostRecent(self, newVideo, channelId): 
        # Do stuff
        return

    def run(self):
        while True:
            driver = webdriver.Firefox() 
            subInfo = self.getChannelAndMostRecent()
            for subId in subInfo:
                newVideos = self.getNewVideosForSub(driver, subId, "")
                if len(newVideos) > 0:
                    self.postInDiscord(newVideos, sub)
            time.sleep(7200)

if __name__ == "__main__":
    yt = Youtube()
    yt.run()

