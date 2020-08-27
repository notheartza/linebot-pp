import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pyrebase


cred = credentials.Certificate("./linebot-pp/linebot-pp-firebase-adminsdk-pkt20-eb15ce9f27.json")
default_app = firebase_admin.initialize_app(cred)
firebase_db = firestore.client()


config = {
  "apiKey": "AIzaSyCO3DgD2x6fJuageulBP9i1l619Ee54beA",
  "authDomain": "linebot-pp.firebaseapp.com",
  "databaseURL": "https://linebot-pp.firebaseio.com/",
  "storageBucket": "linebot-pp.appspot.com",
  "serviceAccount": "./linebot-pp/linebot-pp-firebase-adminsdk-pkt20-eb15ce9f27.json"
}
r_firebase = pyrebase.initialize_app(config)
firebase_rdb = r_firebase.database()