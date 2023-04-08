import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("Exmod.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project-id.firebaseio.com/'
})
