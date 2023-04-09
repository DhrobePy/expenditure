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


    
def login_page():
    st.title("Login")

    users = {
        "admin": {"password": "admin101"},
        "rokon": {"password": "rokon123"},
        "sahosh": {"password": "sahosh345"},
        "talha": {"password": "talha456"},
        "kawsar":{"password": "kawsar567"}
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
    st.title(f"{st.session_state.username} Dashboard")
    
    choice = option_menu(
        options=['Expense Submission', 'Pending Expenses', 'Authorized Expenses', 'Partial Update', 'Performance Report'],
        menu_title=None,
        menu_icon='cast',
        orientation='horizontal'
    )

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

    expense_category = st.selectbox("Expense Category", ["", "Travel", "Food", "Office Supplies", "Rent", "Utilities", "Miscellaneous"])
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
    #add new category 
    new_category = st.text_input("Add a new expense category")
    if st.button("Add Category"):
        if new_category:
            add_expense_category(new_category)
            st.success("New category added")
        else:
            st.error("Please enter a category name")
    
    #Deleting pending expense
    st.subheader("Pending Expenses")
    user_expenses_data = get_user_expenses(st.session_state.username) or {}

    for expense_id, expense in user_expenses_data.items():
        st.write(f"Category: {expense['Category']}, Amount: {expense['Amount']}, Date: {expense['Date']}, Method: {expense['Method']}")
        delete_expense_button = st.button(f"Delete expense {expense_id}")
        if delete_expense_button:
            delete_pending_expense(expense_id)
            st.success(f"Expense {expense_id} deleted")
    #add logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.write("Logging out...")
        return

def admin_dashboard():
    st.title(f"{st.session_state.username} Dashboard")

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
        
    
    
    search_category = st.selectbox("Search by Category", ["", "Travel", "Food", "Office Supplies", "Rent", "Utilities", "Miscellaneous"])
    search_keyword = st.text_input("Search by Keyword")

    all_expenses = get_all_expenses()
    filtered_expenses = []

    for expense in all_expenses:
        if search_category and search_keyword:
            if expense["Category"] == search_category and search_keyword.lower() in expense["Category"].lower():
                filtered_expenses.append(expense)
        elif search_category:
            if expense["Category"] == search_category:
                filtered_expenses.append(expense)
        elif search_keyword:
            if search_keyword.lower() in expense["Category"].lower():
                filtered_expenses.append(expense)

    if filtered_expenses:
        filtered_expenses_df = pd.DataFrame(filtered_expenses, columns=["Username", "Category", "Amount", "Date", "Method", "Submitted"])
        st.write(filtered_expenses_df)
    else:
        st.write("No expenses found")
    
    #show all expense in categories
    if st.button("Show Category-wise Expenses"):
        all_expenses = get_all_expenses()
        expenses_by_category = {}

        for expense in all_expenses:
            category = expense["Category"]
            if category not in expenses_by_category:
                expenses_by_category[category] = []
            expenses_by_category[category].append(expense)

        for category, expenses in expenses_by_category.items():
            st.subheader(f"Category: {category}")
            expenses_df = pd.DataFrame(expenses, columns=["Username", "Category", "Amount", "Date", "Method", "Submitted"])
            st.write(expenses_df)
    #Date Range
    st.subheader("View expenses by date range")
    date_range = st.date_input("Select a date range", [datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])

    if date_range:
        start_date = date_range[0]
        end_date = date_range[1]

        all_expenses = get_all_expenses()
        filtered_expenses = []

        for expense in all_expenses:
            expense_date = datetime.datetime.strptime(expense["Date"], "%Y-%m-%d").date()
            if start_date <= expense_date <= end_date:
                filtered_expenses.append(expense)

        if filtered_expenses:
            filtered_expenses_df = pd.DataFrame(filtered_expenses, columns=["Username", "Category", "Amount", "Date", "Method", "Submitted"])
            st.write(filtered_expenses_df)
        else:
            st.write("No expenses found for the selected date range")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.write("Logging out...")
        return

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

