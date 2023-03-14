import streamlit as st
import pandas as pd
import requests
#response = requests.get(url)

# Set the URL of the Excel file in the Git repository
file_url = "https://github.com/DhrobePy/expenditure/blob/a5ff7a45e75f73522f84539bf153f3210c2112cb/Expenditure.xlsx?raw=true"

#response = requests.get(file_url)
# Read the Excel file into a pandas DataFrame
#df = pd.read_excel(file_url)

#st.write(df)

st.set_page_config(page_title="Add Data to Excel Sheet")

# Define a function to add data to the Excel sheet
def add_data_to_excel(date, item_name, quantity):
    # Load the existing Excel file into a Pandas DataFrame
    df = pd.read_excel(file_url)

    # Add a new row to the DataFrame with the given data
    new_row = {"Date": date, "Item Name": item_name, "Quantity": quantity}
    df = df.append(new_row, ignore_index=True)

    # Write the updated DataFrame back to the Excel file
    df.to_excel('https://github.com/DhrobePy/expenditure/blob/a5ff7a45e75f73522f84539bf153f3210c2112cb/Expenditure.xlsx', index=False)

# Create the Streamlit app
st.title("Add Data to Excel Sheet")

# Create input widgets for each column in the Excel file
date = st.date_input("Date")
item_name = st.text_input("Item Name")
quantity = st.number_input("Quantity", min_value=1)

# Create a button to add the data to the Excel file
if st.button("Add Data"):
    add_data_to_excel(date, item_name, quantity)
    st.success("Data added to Excel sheet!")
