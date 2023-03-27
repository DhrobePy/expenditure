import streamlit as st
from streamlit_option_menu import option_menu
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, time, timedelta
import base64
import streamlit_lottie as st_lottie
import requests
import json
import altair as alt
import plotly.express as px




with open('download_button.json', 'r') as f:
    button_data = f.read()

def create_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="expense_report.csv">Download Expense Report</a>'
    return href
    

def create_products_table():
    data = {
        'Product': ['Rutti','Jora Hati','Ek hati', 'Kobutor','sunflower','E-Atta'],
        'Description': ['Description 1', 'Description 2', 'Description 3', 'Description 4', 'Description 5', 'Description 6'],
        'Stock as of yesterday ': [50, 80, 25, 75, 60, 90],
        'Stock as of Today':[20,30,40,20,30,40],
        'Total Stock Remaining':[70, 110, 65, 95,90,130]
    }
    df = pd.DataFrame(data)
    return df
def edit_products():
    st.title('Edit Products')
    st.write('Here you can view and update details of all products')

    # Retrieve all products from Firestore and create a dictionary
    def get_products():
        products = {}
        for product in db.collection('products').get():
            product_id = product.id
            data = product.to_dict()
            products[product_id] = data
        return products

    # Display the products as a drop-down menu
    products = get_products()
    product_names = [product['Product'] for product in products.values()]
    selected_product_name = st.selectbox('Select a product to edit', options=product_names)

    # Get the selected product's details
    for product_id, product_data in products.items():
        if product_data['Product'] == selected_product_name:
            selected_product_id = product_id
            selected_product = product_data
            break

    # Show the selected product's details in a form, allowing users to edit the values
    product = st.text_input('Product', value=selected_product['Product'])
    description = st.text_area('Description', value=selected_product['Description'])
    stock_yesterday = st.number_input('Stock as of yesterday', value=selected_product['Stock as of yesterday'])
    stock_today = st.number_input('Stock as of Today', value=selected_product['Stock as of Today'])
    total_stock_remaining = stock_yesterday + stock_today

    # Update the selected product in the Firestore database with the new values from the form
    if st.button('Update Product'):
        product_ref = db.collection('products').document(selected_product_id)
        product_ref.update({
            'Product': product,
            'Description': description,
            'Stock as of yesterday': stock_yesterday,
            'Stock as of Today': stock_today,
            'Total Stock Remaining': total_stock_remaining
        })
        st.success('Product updated successfully')

    # Add a button to download the updated products table as a CSV file
    products_df = pd.DataFrame.from_dict(products, orient='index')
    download_href = create_download_link(products_df)
    st.markdown(download_href, unsafe_allow_html=True)



def customer_details():
    st.title('Customer Details')

    # Add a button to read the customer details from an Excel file
    # Add a button to read the customer details from an Excel file
    if st.button('Read Customer Details from Excel'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Due Date'] = pd.to_datetime(df['Due Date'], format='%d-%m-%Y')
        df['Days Overdue'] = (datetime.now().date() - df['Due Date']).dt.days.clip(lower=0)
        df['Amount Due'] = df['Amount Due'].astype(float)
        df['Total Amount Due'] = df['Amount Due'].sum()
        df['Total Amount Due'] = df['Total Amount Due'].astype(float)
    
        # Show the table of customer details
        st.write(df)

    # Add a button to update the customer details
    if st.button('Update Customer Details'):
        # Show the table of customer details with editable cells
        editable_df = df.copy()
        editable_df.set_index('Customer Name', inplace=True)
        st.write(editable_df)

        # Add a button to save the updated customer details
        if st.button('Save Customer Details'):
            # Update the customer details in the Excel file
            editable_df.reset_index(inplace=True)
            editable_df.to_excel('customer_details.xlsx', index=False)

# Add a button to show the table of receivables
    if st.button('Show Receivables'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Due Date'] = pd.to_datetime(df['Due Date'], format='%d-%m-%Y')
        df['Days Overdue'] = (datetime.now().date() - df['Due Date']).dt.days.clip(lower=0)
        df['Amount Due'] = df['Amount Due'].astype(float)
    
        # Show the table of receivables
        receivables_df = df[['Customer Name', 'Due Date', 'Amount Due', 'Days Overdue']]
        st.write(receivables_df)

    # Add a button to update the receivables
    if st.button('Update Receivables'):
        # Show the table of receivables with editable cells
        editable_df = receivables_df.copy()
        editable_df.set_index('Customer Name', inplace=True)
        st.write(editable_df)

        # Add a button to save the updated receivables
        if st.button('Save Receivables'):
            # Update the receivables in the Excel file
            editable_df.reset_index(inplace=True)
            editable_df.to_excel('customer_details.xlsx', index=False)

# Add a button to show the total amount due
    if st.button('Show Total Amount Due'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Amount Due'] = df['Amount Due'].astype(float)
    
        # Show the total amount due
        total_amount_due = df['Amount Due'].sum()
        st.write(f'Total Amount Due: {total_amount_due}')
    
    # Add a button to show customer-wise total bills due
    
    if st.button('Show Customer-wise Total Bills Due'):
        # Read the customer details from the Excel file
        df = pd.read_excel('customer_details.xlsx')
        df['Amount Due'] = df['Amount Due'].astype(float)
    
    # Group the customer details by customer name and show the total bills due for each customer
    customer_groups = df.groupby('Customer Name')
    for customer_name, customer_df in customer_groups:
        total_bills_due = customer_df['Amount Due'].sum()
        st.write







cred = credentials.Certificate("expenses_updated.json")
#firebase_admin.initialize_app(cred)

# Get a reference to the Firestore database
db = firestore.client()


import pandas as pd



# Define username and password
CORRECT_USERNAME = 'Ujjaladmin'
CORRECT_PASSWORD = 'admin101'

# Define the login page
def login():
    # Add a title
    st.title('Login')

    # Add a form with username and password inputs
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    # Add a button to submit the form
    if st.button('Login'):
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            # Set the session state to True
            st.session_state.logged_in = True
        else:
            st.error('Incorrect username or password')

# Define the app sections
def home():
    st.title('Home')

    # Add a horizontal navigation bar for the Home page
    #st.write('Navigation')
    choice = option_menu(
        options=['Products', 'Prices', 'Orders Due', 'Bills Receivables', 'Bills Payables'],
        menu_title=None,
        menu_icon='cast',
        orientation='horizontal')
    #options = ['Products', 'Prices', 'Order Due', 'Bills Due']
    #choice = st.radio('', options)

    # Show the appropriate section based on the user's choice
    if choice == 'Products':
        st.write('Here you can view a list of all products')
        products_df = create_products_table()
        st.write(products_df)
        edit_products()

    elif choice == 'Prices':
        st.header('Prices')
        st.write('Here you can view and update prices for different products')
    elif choice == 'Orders Due':
        st.header('Orders Due')
        st.write('Here you can view a list of all pending orders')
    elif choice=='Bills Receivables':
        st.header('Bills receivables')
        customer_details()
    elif choice == 'Bills Payables':
        st.header('Bills Due')
        st.write('Here you can view a list of all pending bills')

def create_chart(df):
    chart_data = df.groupby('Category')['Amount'].sum()
    chart = alt.Chart(chart_data.reset_index()).mark_bar().encode(
        x=alt.X('Category', sort='-y'),
        y=alt.Y('Amount', title='Total Amount'),
        tooltip=['Category', 'Amount']
    ).properties(
        title='Expenses by Category'
    )
    return chart


def expense():
    st.title('Expense')

    # Add a horizontal navigation bar for the Expense section
    selected = option_menu(
        options=['Add Expense', 'Update Records', 'Expense Summary'],
        menu_title=None,
        menu_icon='cast',
        orientation='horizontal')

    # Show the appropriate section based on the user's choice
    if selected == 'Add Expense':
        st.header('Add Expense')
        expense_date = st.date_input('Date of Expense')
        expense_date_str = expense_date.strftime('%Y-%m-%d')

        # Define a function to insert expense data into the Firestore collection
        # Define a function to insert expense data into the Firestore collection
        def insert_data(category, amount, method, paid_by, remarks, expense_date):
            expense_date_str = expense_date.strftime('%Y-%m-%d')
            now = datetime.now()
            db.collection('expenses').add({
                'category': category,
                'amount': amount,
                'method': method,
                'paid_by': paid_by,
                'remarks': remarks,
                'expense_date': expense_date_str,
                'datetime': now
            })


        # Add a form for the user to enter expense details
        category = st.selectbox('Category of Expense', ['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'])
        amount = st.number_input('Amount of Expense')
        method = st.selectbox('Way of Payment', ['Cash', 'Bank Account Cheque'])
        if method == 'Cash':
            paid_by = st.text_input('Paid By')
        else:
            bank_accounts = ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234']
            paid_by = st.selectbox('Bank Account Number', bank_accounts)

        remarks = st.text_area('Remarks')

        # Add a button to submit the form and insert the data into the Firestore collection
        if st.button('Add Expense'):
            insert_data(category, amount, method, paid_by, remarks, expense_date)
            st.success('Expense added successfully')
    

    elif selected == 'Update Records':
        st.header('Update Records')

    # Retrieve all expenses from Firestore and create a dictionary
        def get_expenses():
            expenses = {}
            for expense in db.collection('expenses').get():
                expense_id = expense.id
                data = expense.to_dict()
                expenses[expense_id] = data
            return expenses

    # Display the expenses as a drop-down menu
        expenses = get_expenses()
        expense_ids = list(expenses.keys())
        expense_names = [f"{expense['category']} - {expense['expense_date']}" for expense in expenses.values()]
        expense_dict = dict(zip(expense_ids, expense_names))
        selected_expense_id = st.selectbox("Select an expense to update", options=expense_ids, format_func=lambda x: expense_dict[x])

    # Get the selected expense's details
        selected_expense = expenses[selected_expense_id]

    # Show the selected expense's details in a form, allowing users to edit the values
        category = st.selectbox('Category of Expense', ['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'], index=['Raw Material Purchase', 'Transportation for Raw Material', 'Manpower for Raw Material Handling', 'Electricity Bill for Raw Material Processing', 'Packaging', 'Transportation to Buyer'].index(selected_expense['category']))
        amount = st.number_input('Amount of Expense', value=float(selected_expense['amount']))
        method = st.selectbox('Way of Payment', ['Cash', 'Bank Account Cheque'], index=['Cash', 'Bank Account Cheque'].index(selected_expense['method']))
        if method == 'Cash':
            paid_by = st.text_input('Paid By', value=str(selected_expense.get('paid_by', '')))
        else:
            bank_accounts = ['1234567890', '2345678901', '3456789012', '4567890123', '5678901234']
            paid_by = st.selectbox('Bank Account Number', bank_accounts, index=bank_accounts.index(str(selected_expense.get('paid_by', ''))))
        remarks = st.text_area('Remarks', value=str(selected_expense.get('remarks', '')))
        expense_date = st.date_input('Date of Expense', value=datetime.strptime(selected_expense['expense_date'], '%Y-%m-%d').date())

    # Update the selected expense in the Firestore database with the new values from the form
        if st.button('Update Expense'):
            expense_ref = db.collection('expenses').document(selected_expense_id)
            expense_date_str = expense_date.strftime('%Y-%m-%d')
            expense_ref.update({
            'category': category,
            'amount': amount,
            'method': method,
            'paid_by': paid_by,
            'remarks': remarks,
            'expense_date': expense_date_str,
        })
            st.success('Expense updated successfully')

    
    
    elif selected == 'Expense Summary':
        st.header('Expense Summary')

    # Add date pickers to select start and end dates
        start_date = st.date_input('Select start date')
        end_date = st.date_input('Select end date', value=datetime.now().date())

    # Add a button to show expenses for the selected period
        if st.button('Show Expense Report'):
        # Define a function to retrieve expense data from the Firestore collection
            def get_expenses():
                expenses = []
                for expense in db.collection('expenses').get():
                    data = expense.to_dict()
                    if 'method' in data:
                        expense_date_str = data.get('expense_date', '')
                        expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date() if expense_date_str else None
                        if expense_date and start_date <= expense_date <= end_date:
                            expenses.append({
                                'Category': data['category'],
                                'Amount': data['amount'],
                                'Payment Method': data['method'],
                                'Paid By': data.get('paid_by', ''),
                                'Description': data.get('remarks', ''),
                                'Date of Expense': expense_date
                            })
                df = pd.DataFrame(expenses)
                total_amount = df['Amount'].sum()
                df = df.append({'Category': 'Total', 'Amount': total_amount}, ignore_index=True)
        
                # Group the expenses by category and show a summary table for each category
                categories = df['Category'].unique()
                for category in categories:
                    if category == 'Total':
                        continue
                    category_df = df[df['Category'] == category]
                    st.subheader(f'{category} Expenses')
                    st.write(category_df)
                    st.write(f'Total Amount: {category_df["Amount"].sum()}')

                # Show the summary table for all expenses
                st.subheader('All Expenses')
                st.dataframe(df)

                expenses_chart_data =df[df['Category'] != 'Total']
                chart = create_chart(expenses_chart_data)
                fig = px.pie(df, values='Amount', names=df.index)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.altair_chart(chart, use_container_width=True)
                with col2:
                    st.plotly_chart(fig)           
                


                # Add a button to download the expense report as a CSV file
                #st.button("Download Expense Summary Report"):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="expense_report.csv">Download Expense Report (CSV)</a>'
                st.markdown(href, unsafe_allow_html=True)

            # Retrieve the expense data for the selected period and display it as a table
            get_expenses()



def costing_pricing():
    st.title('Costing and Pricing')
    st.write('Welcome to the Costing and Pricing section of the app')

def balance_sheet():
    st.title('Balance Sheet')
    st.write('Welcome to the Balance Sheet section of the app')

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Show the appropriate page based on the logged-in state
if not st.session_state.logged_in:
    login()
else:
    # Add a horizontal navigation bar for the app sections
    #st.set_page_config(page_title='App', page_icon=':money_with_wings:')
    #st.write('Navigation')

    selected=option_menu(
        menu_title=None,
        options = ['Home', 'Expense', 'Costing and Pricing', 'Balance Sheet'],
        menu_icon='cast',
        default_index=0,
        orientation='horizontal',
        )
        
    #choice = st.radio('', options)

    # Show the appropriate app section based on the user's choice
    if selected == 'Home':
        home()
    elif selected == 'Expense':
        expense()
    elif selected == 'Costing and Pricing':
        costing_pricing()
    elif selected == 'Balance Sheet':
        balance_sheet()