from datetime import datetime

import requests
import json
import time
import sqlite3
import configparser
import hvac
import logging
import pymongo
import feedparser
import psycopg2


class Youtube:

  links = {}

  dpPath = "./youtube.db"
  configPath = "./youtube.ini"
  channelUrl = "https://www.youtube.com/channel/"
  rssUrl = "https://www.youtube.com/feeds/videos.xml?channel_id="

  def __init__(self):
    # self.config = configparser.ConfigParser()
    # self.config.read(self.configPath)
    logging.basicConfig()
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.DEBUG)

    self.logger.info("Application Starting")

    self.vaultClient = hvac.Client(
      url="http://192.168.73.20:8200",
      token="s.tLWbbS9mBlEcDedkystiYG8P"
    )

    self.channel = self.vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["channel"]
    username = self.vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["db-username"]
    password = self.vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["db-password"]

    postgresUsername = self.vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["postgres-username"]
    postgresPassword = self.vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["postgres-password"]
    self.postgresConnection = conn = psycopg2.connect(
        host="192.168.73.20",
        database="youtube",
        user=postgresUsername,
        password=postgresPassword)

    client = pymongo.MongoClient(
      "mongodb://192.168.73.20:27017",
      username = username,
      password = password
    )
    nestDB = client["nestdb"]
    self.youtubeDB = nestDB["youtube"]

    response = self.youtubeDB.find({}, {"_id":0, "category":1})

    category = {cat["category"] for cat in response if len(cat["category"]) > 1}
    self.links = { cat:self.vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"][cat] for cat in category}

  
  def getChannelAndMostRecent(self):
    cur = self.postgresConnection.cursor()
    cur.execute("""SELECT channelid FROM channels""")
    channelResponse = cur.fetchall()
    mostRecentData = {}
    for channel in channelResponse:
      channelId = channel[0]
      cur.execute("""SELECT  videoid FROM videos WHERE channelid=%(channelId)s""", {'channelId': channelId})
      videosResponse = cur.fetchall()
      videos = [video[0] for video in videosResponse]
      mostRecentData[channelId] = videos      
    cur.close()
    return mostRecentData


  def getNewVideosForSubWithRSS(self, channelId, recentVideos):
    newsFeed = feedparser.parse(self.rssUrl + channelId)
    newVideos = []
    recentVideosIds = recentVideos
    for vidNdx in range(len(newsFeed.entries)):
      videoId = newsFeed.entries[vidNdx].yt_videoid
      published = newsFeed.entries[vidNdx].published
      title = newsFeed.entries[vidNdx].title
      if videoId in recentVideosIds:
        return newVideos
      newVideos.append((videoId, published, title))
    return newVideos
          

  def postInDiscord(self, newVideos, channelId):
    self.logger.info("Posting videos")
    
    response = self.youtubeDB.find({"channelId": channelId},{"_id":0, "category":1})
    category = response[0]["category"]

    if len(category) == 0: return
    url = self.links[category]

    for video in newVideos[::-1]:
      data = {}
      data["content"] = "https://www.youtube.com/watch?v=" + video[0]
      data["username"] = "YoutubeBot"

      result = requests.post(url, data=json.dumps(data), headers={
                          "Content-Type": "application/json"})
                      
      time.sleep(2)

  def updateMostRecent(self, newVideo, channelId): 
    
    cur = self.postgresConnection.cursor()
    # delete old videos
    cur.execute("""DELETE FROM videos WHERE channelid = %(channelId)s""", {'channelId': channelId})
    for video in newVideo:
      cur.execute("""INSERT INTO videos (videoid, channelid, published, videoname) VALUES (%(videoId)s,%(channelId)s,%(published)s,%(videoName)s)""",
        {'videoId': video[0],'channelId': channelId,'published': video[1],'videoName': video[2]})
    cur.close()
    self.postgresConnection.commit()
    response = self.youtubeDB.update_one({"channelId": channelId},{ "$set": { "mostRecentId": newVideo } })

  def getMostRecentTen(self, channelId):
    newsFeed = feedparser.parse(self.rssUrl + channelId)
    videoIds = []
    for vidNdx in range(len(newsFeed.entries)):
      videoId = newsFeed.entries[vidNdx].yt_videoid
      published = newsFeed.entries[vidNdx].published
      title = newsFeed.entries[vidNdx].title
      if len(videoIds) == 10:
        return videoIds
      videoIds.append((videoId, published, title))
    return videoIds
      

  def run(self):
    while True:
      self.logger.info("Starting: " + str(datetime.now()))
      
      subInfo = self.getChannelAndMostRecent()
      print(subInfo)
      for subId in subInfo.keys():
        self.logger.info("Finding new videos for: " + subId)
        newVideos = self.getNewVideosForSubWithRSS(subId, subInfo[subId])
        if len(newVideos) > 0:
          self.updateMostRecent(self.getMostRecentTen(subId), subId)
          # self.postInDiscord(newVideos, subId) 
      self.logger.info("Sleeping: " + str(datetime.now()))
      time.sleep(1800)

if __name__ == "__main__":
    yt = Youtube()
    yt.run()

