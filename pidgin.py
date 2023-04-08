import streamlit as st
import pandas as pd
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin.exceptions import NotFoundError
from firebase_admin import firestore

db = firestore.client()

cred = credentials.Certificate("Exmod.json")
#firebase_admin.initialize_app(cred, {'databaseURL': 'https://your-project-id.firebaseio.com/'})

def push_expense(expense):
    ref = db.reference('/expenses_to_authorize')
    ref.push(expense)

def get_expenses_to_authorize():
    ref = db.reference('/expenses_to_authorize')
    return ref.get()

def remove_expenses_to_authorize():
    ref = db.reference('/expenses_to_authorize')
    ref.delete()

def push_authorized_expense(expense):
    ref = db.reference('/authorized_expenses')
    ref.push(expense)

def get_authorized_expenses():
    ref = db.reference('/authorized_expenses')
    return ref.get()

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

    if "expense_categories" not in st.session_state:
        st.session_state.expense_categories = ["", "Travel", "Food", "Office Supplies", "Rent", "Utilities", "Miscellaneous"]

    new_category = st.text_input("New Expense Category")
    if st.button("Add Category"):
        if new_category:
            st.session_state.expense_categories.append(new_category)
            st.success(f"Added category: {new_category}")
        else:
            st.error("Please enter a category name")

    expense_category = st.selectbox("Expense Category", st.session_state.expense_categories)
    amount = st.number_input("Amount", min_value=0.0, step=0.1)
    expense_date = st.date_input("Expense Date", datetime.date.today())
    expense_method = st.selectbox("Expense Method", ["", "Cash", "Credit Card", "Debit Card", "Bank Transfer"])

    if st.button("Submit Expense"):
        if expense_category and amount > 0 and expense_method:
            new_expense = {
                "Username": st.session_state.username,
                "Category": expense_category,
                "Amount": amount,
                "Date": expense_date.isoformat(),
                "Method": expense_method,
                "Submitted": datetime.datetime.now().isoformat(),
            }
            push_expense(new_expense)
            st.success("Expense submitted")
        else:
            st.error("Please fill in all fields")

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
        if st.button("Authorize All"):
            authorized_expenses = [
                {**expense, "Authorized": datetime.datetime.now().isoformat()} for expense in expenses_to_authorize
            ]
            for expense in authorized_expenses:
                push_authorized_expense(expense)
            remove_expenses_to_authorize()
            st.success("All expenses authorized")

    if not authorized_expenses_df.empty:
        st.subheader("Authorized Expenses")
        st.write(authorized_expenses_df)

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.username == "admin":
        admin_dashboard()
    else:
        user_dashboard()

if __name__ == "__main__":
    main()

