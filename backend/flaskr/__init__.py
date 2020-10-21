import os
import hvac
import pymongo

from flask import Flask
from flask_mongoengine import MongoEngine
import mongoengine as me
from .Subs import Subs


def create_app():
    app = Flask(__name__)

    vaultClient = hvac.Client(
        url="http://192.168.73.20:8200",
        token="s.tLWbbS9mBlEcDedkystiYG8P"
    )

    username = vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["db-username"]
    password = vaultClient.secrets.kv.read_secret_version(path="youtube")["data"]["data"]["db-password"]

    # app.config["MONGODB_SETTING"] = {
    #     "db": "nestdb",
    #     "host": "mongodb://192.168.73.20:27017",
    #     "username": username,
    #     "password": password
    # }

    # db = MongoEngine(app)
  
    client = pymongo.MongoClient(
        "mongodb://192.168.73.20:27017",
        username = username,
        password = password
    )
    nestDB = client["nestdb"]
    youtubeDB = nestDB["youtube"]

    # Config stuff...

    @app.route("/hello")
    def hello():
        response = youtubeDB.find({},{"_id":0, "channelId":1, "mostRecentId":1})
        return {channel["channelId"]:channel["mostRecentId"] for channel in response}
    return app
