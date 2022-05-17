import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pyrebase

#<----clound firestore--->
cred = credentials.Certificate("./linebot-pp/linebot-pp-firebase-adminsdk-pkt20-eb15ce9f27.json")
default_app = firebase_admin.initialize_app(cred)
firebase_db = firestore.client()

#<----realtime firebase--->
config = {
  "apiKey": "Key",
  "authDomain": "Domain",
  "databaseURL": "URL",
  "storageBucket": "Bucket",
  "serviceAccount": "json"
}
r_firebase = pyrebase.initialize_app(config)
firebase_rdb = r_firebase.database()
