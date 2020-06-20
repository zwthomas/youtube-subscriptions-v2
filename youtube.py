from bs4 import BeautifulSoup
import requests
from selenium import webdriver


driver = webdriver.Firefox() 
channel = "https://www.youtube.com/channel/"
linus = "UCXuqSBlHAE6Xw-yeJA0Tunw"
driver.get(channel + linus)