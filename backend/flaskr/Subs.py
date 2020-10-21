import mongoengine as me 

class Subs(me.Document):
    channelId = me.StringField(required=True)
    channelName = me.StringField()
    category = me.StringField()
    mostRecentId = me.StringField()