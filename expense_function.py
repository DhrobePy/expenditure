import streamlit as st
import pandas as pd
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin.exceptions import NotFoundError
from firebase_admin import firestore
from streamlit_option_menu import option_menu


cred = credentials.Certificate("Exmod.json")
#firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-project-id.firebaseio.com/'})
db = firestore.client()


def get_user_expenses(username):
    expenses_ref = db.collection("expenses")
    expenses_docs = expenses_ref.where("Username", "==", username).stream()
    expenses = {doc.id: doc.to_dict() for doc in expenses_docs}
    return expenses
