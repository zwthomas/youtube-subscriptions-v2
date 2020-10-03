from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import requests
import json
import time
import sqlite3
import configparser

class Youtube:

    

    dpPath = "./youtube.db"
    configPath = "./youtube.ini"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath)
    
    def getChannelAndMostRecent(self):
        conn = sqlite3.connect(self.dpPath)
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
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.XPATH, "//paper-tab/div")))

        elements = driver.find_elements_by_xpath("//paper-tab/div")
        for el in elements:
            if "Videos" in el.get_attribute("innerHTML"):
                el.click()
                break

        # Wait for videos to load
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.TAG_NAME, "ytd-channel-sub-menu-renderer")))
        time.sleep(1)
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
            print("https://www.youtube.com/watch?v=" + videoId)
            if recentVideo == videoId:
                return newVideos
            
            newVideos.append(videoId)
        return newVideos
           

    def postInDiscord(self, newVideos, channelId):
        # self.updateMostRecent(newVideos[0], channelId)

        conn = sqlite3.connect("./youtube.db")
        c = conn.cursor()

        c.execute("SELECT category FROM subs WHERE channelId=?", (channelId,))
        category = c.fetchone()
        if len(category[0]) == 0: return
        url = self.links[category[0]]

        for video in newVideos[::-1]:
            data = {}
            data["content"] = "https://www.youtube.com/watch?v=" + video
            data["username"] = "YoutubeBot"

            result = requests.post(url, data=json.dumps(data), headers={
                                "Content-Type": "application/json"})
                            
            time.sleep(2)
        
        conn.commit()
        conn.close()

    def updateMostRecent(self, newVideo, channelId): 
        conn = sqlite3.connect("./youtube.db")
        c = conn.cursor()

        c.execute("UPDATE subs SET mostRecentId=? WHERE channelId=?", (newVideo, channelId))

        conn.commit()
        conn.close()

    def run(self):
        while True:
            # options = Options()
            # options.headless = True
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("window-size=1920,1080")
            chrome_prefs = {}
            chrome_options.experimental_options["prefs"] = chrome_prefs
            chrome_prefs["profile.default_content_settings"] = {"images": 2} 

            driver  = webdriver.Chrome(options=chrome_options)
            subInfo = self.getChannelAndMostRecent()
            for subId in subInfo:
                newVideos = self.getNewVideosForSub(driver, subId, "")
                if len(newVideos) > 0:
                    self.postInDiscord(newVideos, subId)
            time.sleep(7200)

if __name__ == "__main__":
    yt = Youtube()
    yt.run()

