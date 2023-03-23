
access_token='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'



import streamlit as st
import pandas as pd
import requests

# Set your GitHub username and personal access token
username = "your_username"
access_token = "your_access_token"

# Set the owner and repository name for the repository you want to fork
owner = "DhrobePy"
repo = "expenditure"

# Set the forked repository name
forked_repo = "expenditure_fork"

# Set the API endpoint for forking a repository
api_url = "https://api.github.com/repos/{owner}/{repo}/forks"

# Set the headers for the API request
headers = {"Authorization": f"Token {access_token}"}

# Set the data for the API request
data = {"organization": username, "name": forked_repo}

# Send the API request to fork the repository
response = requests.post(api_url.format(owner=owner, repo=repo), headers=headers, data=data)

# Check if the fork was successful
if response.status_code == 202:
    st.success("Repository forked successfully!")
else:
    st.error("Error forking repository: ", response.text)

# Set the URL of the Excel file in the forked repository
file_url = f"https://raw.githubusercontent.com/{username}/{forked_repo}/main/expenditures.xlsx"
update_file = f"https://raw.githubusercontent.com/{username}/{forked_repo}/main/extras.xlsx"

# Define a function to add data to the Excel sheet
def add_data_to_excel(date, item_name, quantity):
    # Load the existing Excel file into a Pandas DataFrame
    df = pd.read_excel(file_url)

    # Add a new row to the DataFrame with the given data
    new_row = {"Date": date, "Item Name": item_name, "Quantity": quantity}
    df = df.append(new_row, ignore_index=True)

    # Write the updated DataFrame back to the Excel file
    df.to_excel(update_file, index=False)

    # Show a success message
    st.success("Data added to Excel sheet!")
    
    # Reload the updated DataFrame and display it in Streamlit
    df1 = pd.read_excel(file_url)
    st.write(df1)

# Create the Streamlit app
st.title("Add Data to Excel Sheet")

# Create input widgets for each column in the Excel file
date = st.date_input("Date")
item_name = st.text_input("Item Name")
quantity = st.number_input("Quantity", min_value=1)

# Create a button to add the data to the Excel file
if st.button("Add Data"):
    add_data_to_excel(date, item_name, quantity)

    
