import sqlite3
import hvac
import time
import logging
import pymongo

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class YoutubeSetup():
    
    URL = "https://www.youtube.com/channel/{}/channels"
    SUB_URL = "https://www.youtube.com"

    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

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

        # data = [
        #     {"channelId":"UCftcLVz-jtPXoH3cWUUDwYw","channelName":"Bitwit", "category":"tech","mostRecentId":"I98C_zTxUv8"}
        # ]

        # self.youtubeDB.insert_one({"channelId":"UCftcLVz-jtPXoH3cWUUDwYw","channelName":"Bitwit", "category":"tech","mostRecentId":"I98C_zTxUv8"})

        # input("waiting")

        
        
    def run(self):
        self.logger.info("Init Driver")

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("window-size=1920,1080")
        # chrome_prefs = {}
        # chrome_options.experimental_options["prefs"] = chrome_prefs
        # chrome_prefs["profile.default_content_settings"] = {"images": 2} 



        driver  = webdriver.Chrome(options=chrome_options)
        driver.get(self.URL.format(self.channel))
        self.getChannels(driver)
    
    def insertIntoDB(self, channelInfo, mostRecent):
        for channel in channelInfo.keys():
            self.youtubeDB.insert_one({"channelSlug": channelInfo[channel],"channelName": channel, "category":"","mostRecentId":mostRecent[channel]})

    
    def getChannels(self, driver):
        self.logger.info("Getting Channel Data")
        # driver.findElement(By.cssSelector("body")).sendKeys(Keys.CONTROL, Keys.END);
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.ID, "channel")))
        self.loadAllSubs(driver)
        channelInfo = self.getChannelLinks(driver)
        mostRecent = self.getMostRecentVideo(driver, channelInfo)
        self.insertIntoDB(channelInfo, mostRecent)

    def loadAllSubs(self, driver):
        self.logger.info("Loading All Subs")
        prevNum = 0
        numChannels = len(driver.find_elements_by_id("channel"))

        while(prevNum < numChannels):
            prevNum = numChannels
            driver.find_element_by_css_selector("body").send_keys(Keys.CONTROL, Keys.END)
            time.sleep(2)
            numChannels = len(driver.find_elements_by_id("channel"))
    
    def getChannelLinks(self, driver):
        channelInfo = {}
        channels = driver.find_elements_by_id("channel")
        for channel in channels:
            soup = BeautifulSoup(channel.get_attribute("innerHTML"), 'html.parser')
            channelLink = soup.find("a")["href"]
            name = soup.find("span", {"id":"title"}).contents[0]
            channelInfo[name] = channelLink
        return channelInfo

    # def getMostRecentVid(self, driver, channelId, recentVideo):

    #     channel = "https://www.youtube.com/channel/"
    #     driver.get(channel + channelId)

    #     # Nav to video tab
    #     WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.XPATH, "//paper-tab/div")))

    #     elements = driver.find_elements_by_xpath("//paper-tab/div")
    #     for el in elements:
    #         if "Videos" in el.get_attribute("innerHTML"):
    #             el.click()
    #             break

    #     # Wait for videos to load
    #     WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.TAG_NAME, "ytd-channel-sub-menu-renderer")))
    #     time.sleep(1)
    #     # Get all the uploaded videos. Iterate through them until we find the previous most recent vide
    #     newVideos = []
    #     elements = driver.find_elements_by_xpath("//ytd-grid-video-renderer/div")
    #     for el in elements:
    #         try:
    #             anchors = el.find_elements_by_tag_name("a")
    #         except:
    #             self.logger.error(el)

    #         if len(anchors) == 0: continue

    #         videoId = anchors[0].get_attribute("href").split("=")[-1]
    #         # print("https://www.youtube.com/watch?v=" + videoId)
    #         if recentVideo == videoId:
    #             return newVideos
            
    #         newVideos.append(videoId)
    #     return newVideos
    
    def getMostRecentVideo(self, driver, channelInfo):
        mostRecent = {}
        for channel in channelInfo:
            driver.get(self.SUB_URL + channelInfo[channel])
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
            
            elements = driver.find_elements_by_xpath("//ytd-grid-video-renderer/div")
            try:
                anchors = elements[0].find_elements_by_tag_name("a")
            except:
                self.logger.error(elements[0])


            videoId = anchors[0].get_attribute("href").split("=")[-1]
            mostRecent[channel] = videoId
        return mostRecent
            

if __name__ == "__main__":
    ytSetup = YoutubeSetup()
    ytSetup.run()