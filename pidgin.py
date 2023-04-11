import streamlit as st
import pandas as pd
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin.exceptions import NotFoundError
from firebase_admin import firestore
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid


from expense_function import *



cred = credentials.Certificate("Exmod.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

from firebase_admin import firestore

# Set up Firestore connection


# Firestore interaction functions
def push_expense(expense):
    db.collection("expenses_to_authorize").add(expense)

def get_expenses_to_authorize():
    return {doc.id: doc.to_dict() for doc in db.collection("expenses_to_authorize").stream()}

def push_authorized_expense(expense):
    db.collection("authorized_expenses").add(expense)

def get_authorized_expenses():
    return {doc.id: doc.to_dict() for doc in db.collection("authorized_expenses").stream()}

def remove_expenses_to_authorize(doc_id):
    db.collection("expenses_to_authorize").document(doc_id).delete()

def get_user_expenses(username):
    return {doc.id: doc.to_dict() for doc in db.collection("authorized_expenses").where("Username", "==", username).stream()}

def delete_expense(doc_id):
    db.collection("expenses_to_authorize").document(doc_id).delete()

def update_expense(doc_id, updated_expense):
    db.collection("user_expenses").document(doc_id).set(updated_expense)


# Streamlit functions for login, user dashboard, and admin dashboard
def login_page():
    st.title("Login")

    users = {
        "admin": {"password": "admin101"},
        "rokon": {"password": "rokon123"},
        "Sahosh": {"password": "sahosh234"},
        "Talha": {"password": "talha345"},
        "Kawser": {"password": "kawser456"},
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

    col1, col2, col3 = st.columns(3)

    # First expander: Approved user expenses
    with col1.expander("Approved Expenses"):
        user_expenses_data = get_user_expenses(st.session_state.username)
        user_expenses = list(user_expenses_data.values())
        user_expenses_df = pd.DataFrame(user_expenses, columns=["Category", "Amount", "Date", "Method", "Submitted", "Authorized"])

        if not user_expenses_df.empty:
            st.write(user_expenses_df)
        else:
            st.write("No approved expenses")

    # Second expander: Add expense for submission
    with col2.expander("Add Expense"):
        category = st.selectbox("Expense Category", ["Raw Material", "Transport", "Utility", "Repair", "Rent"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        expense_date = st.date_input("Expense Date", datetime.date.today())
        method = st.selectbox("Expense Method", ["Cash", "Bank Account"])

        if method == "Cash":
            cash_deducted_by = st.text_input("Cash Deducted By")
        elif method == "Bank Account":
            bank_account = st.selectbox("Bank Account", [f"Bank Account {i}" for i in range(1, 11)])

        if st.button("Submit Expense"):
            expense = {
                "Username": st.session_state.username,
                "Category": category,
                "Amount": amount,
                "Date": expense_date.isoformat(),
                "Method": method,
                "Submitted": datetime.datetime.now().isoformat(),
            }
            if method == "Cash":
                expense["Cash Deducted By"] = cash_deducted_by
            elif method == "Bank Account":
                expense["Bank Account"] = bank_account

            push_expense(expense)
            st.success("Expense submitted for authorization")

    # Logout button below the second expander
    

    # Third expander: Pending expenses for authorization
    with col3.expander("Pending Expenses"):
        expenses_to_authorize_data = get_expenses_to_authorize()
        expenses_to_authorize = [
            {**expense, "doc_id": doc_id} for doc_id, expense in expenses_to_authorize_data.items()
            if expense["Username"] == st.session_state.username
        ]
        expenses_to_authorize_df = pd.DataFrame(expenses_to_authorize, columns=["Category", "Amount", "Date", "Method", "Submitted"])

        if not expenses_to_authorize_df.empty:
            for i, expense in enumerate(expenses_to_authorize):
                submitted_datetime = datetime.datetime.fromisoformat(expense['Submitted'])
                submitted_formatted = submitted_datetime.strftime("%Y-%m-%d, %A, %H:%M")
                st.write(f"{i + 1}. {expense['Category']}, {expense['Amount']}, {expense['Date']}, {expense['Method']}, {submitted_formatted}")
                if st.button(f"Delete Expense {i + 1}"):
                    delete_expense(expense["doc_id"])
                    st.success("Expense deleted")
        else:
            st.write("No pending expenses for authorization")
            
    
    with col1.expander("Update Approved Expenses"):
        if not user_expenses_df.empty:
            editable_expenses_df = pd.DataFrame(user_expenses, columns=["Category", "Amount", "Date", "Method", "Submitted", "Authorized"])
            grid_response = AgGrid(editable_expenses_df, editable=True, fit_columns_on_grid_load=True)
            updated_expenses = grid_response['data']

            if st.button("Update Expenses"):
                if updated_expenses is not None:
                    updated_expenses_df = pd.DataFrame(updated_expenses)
                    for index, row in updated_expenses_df.iterrows():
                        doc_id = list(user_expenses_data.keys())[int(index)]
                        updated_expense = row.to_dict()
                        update_expense(doc_id, updated_expense)
                    st.success("Expenses updated")
                else:
                    st.warning("No expenses to update")
        else:
            st.write("No approved expenses to update")


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
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.write("Logging out...")
        return
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

 
