import streamlit as st
import pandas as pd
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin.exceptions import NotFoundError
from firebase_admin import firestore
from streamlit_option_menu import option_menu

from expense_function import *



cred = credentials.Certificate("Exmod.json")
#firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-project-id.firebaseio.com/'})
db = firestore.client()



# Firebase interaction functions
def push_expense(expense):
    ref = db.reference("/expenses_to_authorize")
    ref.push(expense)

def get_expenses_to_authorize():
    ref = db.reference("/expenses_to_authorize")
    return ref.get()

def push_authorized_expense(expense):
    ref = db.reference("/authorized_expenses")
    ref.push(expense)

def get_authorized_expenses():
    ref = db.reference("/authorized_expenses")
    return ref.get()

def remove_expenses_to_authorize(doc_id):
    ref = db.reference(f"/expenses_to_authorize/{doc_id}")
    ref.delete()

def get_user_expenses(username):
    ref = db.reference("/authorized_expenses")
    expenses = ref.order_by_child("Username").equal_to(username).get()
    return expenses

# Streamlit functions for login, user dashboard, and admin dashboard
def login_page():
    st.title("Login")

    users = {
        "admin": {"password": "admin101"},
        "maker1": {"password": "maker123"},
        "user3": {"password": "user3pass"},
        "user4": {"password": "user4pass"},
    }

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.success(f"Logged in as {username}")
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password")

def user_dashboard():
    st.title("User Dashboard")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.write("Logging out...")
        return

    user_expenses_data = get_user_expenses(st.session_state.username) or {}
    user_expenses = [expense for expense in user_expenses_data.values()]
    user_expenses_df = pd.DataFrame(user_expenses, columns=["Category", "Amount", "Date", "Method", "Submitted"])

    if not user_expenses_df.empty:
        st.subheader("Your Expenses")
        st.write(user_expenses_df)

        search_option = st.selectbox("Search expenses by", ["All expenses", "Date"])
        if search_option == "Date":
            search_date = st.date_input("Select a date", datetime.date.today())
            filtered_expenses_df = user_expenses_df[user_expenses_df['Date'] == search_date.isoformat()]
            st.write(filtered_expenses_df)
        else:
            st.write(user_expenses_df)

    # Adding new expenses
    # ...

def admin_dashboard():
    st.title("Admin Dashboard")

    expenses_to_authorize_data = get_expenses_to_authorize() or {}
    expenses_to_authorize = [expense for expense in expenses_to_authorize_data.values()]
    expenses_to_authorize_df = pd.DataFrame(expenses_to_authorize, columns=["Username", "Category", "Amount", "Date", "Method", "Submitted"])

    authorized_expenses_data = get_authorized_expenses() or {}
    authorized_expenses = [expense for expense in authorized_expenses_data.values()]
    authorized_expenses_df = pd.DataFrame(authorized_expenses, columns=["Username", "Category", "Amount", "Date", "Method", "Submitted", "Authorized"])

    if not expenses_to_authorize_df.empty:
        st.subheader("Expenses to Authorize")
        st.write(expenses_to_authorize_df)

        col1, col2 = st.columns(2)
        if col1.button("Authorize All"):
            authorized_expenses = [
                {**expense, "Authorized": datetime.datetime.now().isoformat()} for expense in expenses_to_authorize
            ]
            for expense in authorized_expenses:
                push_authorized_expense(expense)
            for doc_id in expenses_to_authorize_data.keys():
                remove_expenses_to_authorize(doc_id)
            st.success("All expenses authorized")

        if col2.button("Reject All"):
            for doc_id in expenses_to_authorize_data.keys():
                remove_expenses_to_authorize(doc_id)
            st.success("All expenses rejected")

    if not authorized_expenses_df.empty:
        st.subheader("Authorized Expenses")
        st.write(authorized_expenses_df)

# Streamlit app execution
def main():
    st.set_page_config(page_title="Expense Tracker", layout="wide")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        if st.session_state.username == "admin":
            admin_dashboard()
        else:
            user_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()

 
