import streamlit as st
import pandas as pd
import datetime

# Dictionary for storing user information (for demonstration purposes only)
USERS = {
    "admin": {"password": "admin101"},
    "maker1": {"password": "maker123"},
    "user3": {"password": "user3pass"},
    "user4": {"password": "user4pass"},
}

def admin_dashboard():
    st.title("Admin Dashboard")

    if "expenses_to_authorize" not in st.session_state:
        st.session_state.expenses_to_authorize = []

    if "authorized_expenses" not in st.session_state:
        st.session_state.authorized_expenses = []

    expenses_to_authorize_df = pd.DataFrame(st.session_state.expenses_to_authorize, columns=["Username", "Category", "Amount", "Date", "Method"])
    authorized_expenses_df = pd.DataFrame(st.session_state.authorized_expenses, columns=["Username", "Category", "Amount", "Date", "Method"])

    if not expenses_to_authorize_df.empty:
        st.subheader("Expenses to Authorize")
        st.write(expenses_to_authorize_df)
        if st.button("Authorize All"):
            st.session_state.authorized_expenses.extend(st.session_state.expenses_to_authorize)
            st.session_state.expenses_to_authorize = []
            st.success("All expenses authorized")

    if not authorized_expenses_df.empty:
        st.subheader("Authorized Expenses")
        st.write(authorized_expenses_df)

def user_dashboard():
    st.title("User Dashboard")

    # Add a logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.write("Logged out successfully. Redirecting to the login page...")

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
                "Date": expense_date,
                "Method": expense_method,
            }
            st.session_state.expenses_to_authorize.append(new_expense)
            st.success("Expense submitted")
        else:
            st.error("Please fill in all fields")



def dashboard():
    if st.session_state.username == "admin":
        admin_dashboard()
    else:
        user_dashboard()

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Logged in as {username}")
            st.write("Redirecting to the dashboard...")
        else:
            st.error("Invalid username or password")

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "expenses_to_authorize" not in st.session_state:
        st.session_state.expenses_to_authorize = []

    if "authorized_expenses" not in st.session_state:
        st.session_state.authorized_expenses = []

    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()

