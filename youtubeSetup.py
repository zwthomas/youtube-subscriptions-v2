import sqlite3
import google_auth_oauthlib.flow
import googleapiclient.errors
import googleapiclient.discovery
import hvac
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class YoutubeSetup():
    
    URL = "https://www.youtube.com/channel/{}/channels"

    def __init__(self):
        vaultClient = hvac.Client(
            url="http://192.168.73.20:8200",
            token="s.tLWbbS9mBlEcDedkystiYG8P"
        )
        self.channel = vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["channel"]
        print(self.channel)

    def run(self):
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
    
    def getChannels(self, driver):
        # driver.findElement(By.cssSelector("body")).sendKeys(Keys.CONTROL, Keys.END);
        WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.ID, "channel")))

        driver.find_element_by_css_selector("body").send_keys(Keys.CONTROL, Keys.END)
        time.sleep(2)
        channels = driver.find_elements_by_id("channel")
        print(len(channels))

if __name__ == "__main__":
    ytSetup = YoutubeSetup()
    ytSetup.run()