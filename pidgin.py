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

def push_expense(expense):
    db.collection('expenses_to_authorize').add(expense)

def get_expenses_to_authorize():
    docs = db.collection('expenses_to_authorize').stream()
    return {doc.id: doc.to_dict() for doc in docs}

def remove_expenses_to_authorize(doc_id):
    db.collection('expenses_to_authorize').document(doc_id).delete()

def push_authorized_expense(expense):
    db.collection('authorized_expenses').add(expense)

def get_authorized_expenses():
    docs = db.collection('authorized_expenses').stream()
    return {doc.id: doc.to_dict() for doc in docs}

def get_all_expenses():
    expenses = []

    # Fetch expenses_to_authorize
    col_ref = db.collection('expenses_to_authorize')
    docs = col_ref.stream()
    for doc in docs:
        expenses.append(doc.to_dict())

    # Fetch authorized_expenses
    col_ref = db.collection('authorized_expenses')
    docs = col_ref.stream()
    for doc in docs:
        expenses.append(doc.to_dict())

    return expenses

def add_expense_category(category):
    col_ref = db.collection('expense_categories')
    col_ref.add({"category": category})


def delete_pending_expense(expense_id):
    col_ref = db.collection('expenses_to_authorize')
    col_ref.document(expense_id).delete()

def format_expense(expense):
    return f"{expense['Category']} - {expense['Amount']} - {expense['Date']} - {expense['Method']}"

def get_method_index(method):
    methods = ["Cash", "Credit Card", "Debit Card", "Bank Transfer"]
    return methods.index(method)

# Replace update_expense with your actual implementation for updating expenses
def update_expense(expense_id, updated_expense):
    pass
    
    
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


def get_user_expenses(username):
    col_ref = db.collection('expenses_to_authorize')
    query_ref = col_ref.where('Username', '==', username)
    docs = query_ref.stream()

    user_expenses = {}
    for doc in docs:
        user_expenses[doc.id] = doc.to_dict()

    return user_expenses


def submit_expense_choice():
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
            
def authorized_expenses_all():
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
            
def pending_expenses():
    st.subheader("Pending Expenses")
    user_expenses_data = get_user_expenses(st.session_state.username) or {}

    for expense_id, expense in user_expenses_data.items():
        st.write(f"Category: {expense['Category']}, Amount: {expense['Amount']}, Date: {expense['Date']}, Method: {expense['Method']}")
        delete_expense_button = st.button(f"Delete expense {expense_id}")
        if delete_expense_button:
            delete_pending_expense(expense_id)
            st.success(f"Expense {expense_id} deleted")
            
def add_category():
    new_category = st.text_input("Add a new expense category")
    if st.button("Add Category"):
        if new_category:
            add_expense_category(new_category)
            st.success("New category added")
        else:
            st.error("Please enter a category name")

def partial_update():
    st.subheader("Edit Authorized Expenses")
    user_expenses_data = get_user_expenses(st.session_state.username) or {}
    user_approved_expenses = [expense for expense in user_expenses_data.values() if expense["is_approved"]]
    expense_to_edit = st.selectbox("Select an expense to edit", user_approved_expenses, format_func=format_expense)
        
    if expense_to_edit:
        expense_category = st.text_input("Expense Category", expense_to_edit["Category"])
        amount = st.number_input("Amount", min_value=0.0, step=0.1, value=expense_to_edit["Amount"])
        expense_date = st.date_input("Expense Date", datetime.datetime.strptime(expense_to_edit["Date"], "%Y-%m-%d").date())
        expense_method = st.selectbox("Expense Method", ["Cash", "Credit Card", "Debit Card", "Bank Transfer"], index=get_method_index(expense_to_edit["Method"]))
        
        if st.button("Update Expense"):
            if expense_category and amount > 0 and expense_method:
                updated_expense = {
                        "Username": st.session_state.username,
                        "Category": expense_category,
                        "Amount": amount,
                        "Date": expense_date.isoformat(),
                        "Method": expense_method,
                        "Submitted": datetime.datetime.now().isoformat(),
                        "is_approved": False,
                    }
                update_expense(expense_to_edit["id"], updated_expense)
                st.success("Expense updated and awaiting approval")
            else:
                st.error("Please fill in all fields")

                
def au_all():
    st.subheader("Your Authorized Expenses")
    user_expenses_data = get_user_expenses(st.session_state.username) or {}
    user_authorized_expenses = [expense for expense in user_expenses_data.values() if expense["is_approved"]]
    user_authorized_expenses_df = pd.DataFrame(user_authorized_expenses, columns=["Category", "Amount", "Date", "Method", "Submitted", "Authorized"])
    if not user_authorized_expenses_df.empty:
        st.write(user_authorized_expenses_df)
    else:
        st.write("No authorized expenses to display")

                
def user_dashboard():
    st.title(f"{st.session_state.username} Dashboard")
    
    choice = option_menu(
        options=['Expense Submission', 'Pending Expenses', 'Authorized Expenses', 'Partial Update', 'Performance Report'],
        menu_title=None,
        menu_icon='cast',
        orientation='horizontal'
    )
    
    if choice=="Expense Submission":
        st.write("Lets Submit new expense")
        submit_expense_choice()
        st.title("Add a New Category for clear expense tracking")
        add_category()
        
    if choice == "Pending Expenses":
        st.subheader("Your Pending Expenses")

        if st.button("Show Pending Expenses"):
            user_expenses_data = get_user_expenses(st.session_state.username) or {}
            user_pending_expenses = [expense for expense in user_expenses_data.values() if not expense.get("is_approved", False)]


            user_pending_expenses_df = pd.DataFrame(user_pending_expenses, columns=["Category", "Amount", "Date", "Method", "Submitted"])

            if not user_pending_expenses_df.empty:
                st.write(user_pending_expenses_df)
            else:
                st.write("No pending expenses to display")
        
    if choice == "Authorized Expenses":
        st.write("Here is your all expenses that has been approved")
        authorized_expenses_all()
        au_all()
        
    if choice == "Partial Update":
        st.subheader("Update Your Authorized Expenses")

        user_expenses_data = get_user_expenses(st.session_state.username) or {}
        user_authorized_expenses = [expense for expense in user_expenses_data.values() if expense.get("is_approved", False)]

        if user_authorized_expenses:
            expense_options = [f"{expense['Category']} - {expense['Amount']} - {expense['Date']}" for expense in user_authorized_expenses]
            selected_expense = st.selectbox("Select an authorized expense to update", expense_options)
            expense_index = expense_options.index(selected_expense)
            expense_id = list(user_expenses_data.keys())[expense_index]

            category = st.selectbox("Expense Category", ["", "Travel", "Food", "Office Supplies", "Rent", "Utilities", "Miscellaneous"], index=expense_options.index(user_authorized_expenses[expense_index]["Category"]))
            amount = st.number_input("Amount", min_value=0.0, step=0.1, value=user_authorized_expenses[expense_index]["Amount"])
            date = st.date_input("Expense Date", datetime.date.fromisoformat(user_authorized_expenses[expense_index]["Date"]))
            method = st.selectbox("Expense Method", ["", "Cash", "Credit Card", "Debit Card", "Bank Transfer"], index=expense_options.index(user_authorized_expenses[expense_index]["Method"]))

            if st.button("Update Expense"):
                updated_expense = {
                    "Category": category,
                    "Amount": amount,
                    "Date": date.isoformat(),
                    "Method": method,
                    "is_approved": False,  # Set to pending authorization
                }
                update_expense(expense_id, updated_expense)
                st.success("Expense updated and awaiting authorization")
        else:
            st.write("No authorized expenses to display")

        
       
        
    

    
    
    #Submit Expense Function:
    
    #add new category 
    
    
    #Deleting pending expense
    
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

