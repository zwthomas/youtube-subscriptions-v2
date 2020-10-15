from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from datetime import datetime

import requests
import json
import time
import sqlite3
import configparser
import hvac
import logging
import pymongo


class Youtube:

    links = {}

    dpPath = "./youtube.db"
    configPath = "./youtube.ini"
    channelUrl = "https://www.youtube.com/channel/"

    def __init__(self):
        # self.config = configparser.ConfigParser()
        # self.config.read(self.configPath)
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.logger.info("Application Starting")

        vaultClient = hvac.Client(
            url="http://192.168.73.20:8200",
            token="s.tLWbbS9mBlEcDedkystiYG8P"
        )

        self.channel = vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["channel"]
        username = vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["db-username"]
        password = vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["db-password"]

        client = pymongo.MongoClient(
            "mongodb://192.168.73.20:27017",
            username = username,
            password = password
        )
        nestDB = client["nestdb"]
        self.youtubeDB = nestDB["youtube"]

        response = self.youtubeDB.find({}, {"_id":0, "category":1})

        category = {cat["category"] for cat in response if len(cat["category"]) > 1}
        self.links = { cat:vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"][cat] for cat in category}

    
    def getChannelAndMostRecent(self):
        response = self.youtubeDB.find({},{"_id":0, "channelId":1, "mostRecentId":1})
        data = {channel["channelId"]:channel["mostRecentId"] for channel in response}
        print(data)
        input()
        # subInfo = {sub[0]: sub[1] for sub in c.fetchall()}

        # conn.commit()
        # conn.close()

        # return subInfo

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
                self.logger.error(el)

            if len(anchors) == 0: continue

            videoId = anchors[0].get_attribute("href").split("=")[-1]
            # print("https://www.youtube.com/watch?v=" + videoId)
            if recentVideo == videoId:
                return newVideos
            
            newVideos.append(videoId)
        return newVideos
           

    def postInDiscord(self, newVideos, channelId):
        self.logger.info("Posting videos")
        self.updateMostRecent(newVideos[0], channelId)

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
            self.logger.info("Starting: " + str(datetime.now()))
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
                self.logger.info("Finding new videos for: " + subId)
                newVideos = self.getNewVideosForSub(driver, subId, subInfo[subId])
                if len(newVideos) > 0:
                    self.postInDiscord(newVideos, subId)
            driver.close() 
            driver.quit()
            self.logger.info("Sleeping: " + str(datetime.now()))
            time.sleep(7200)

if __name__ == "__main__":
    yt = Youtube()
    yt.run()

