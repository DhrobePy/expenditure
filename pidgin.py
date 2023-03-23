import streamlit as st
import pandas as pd
import requests
#response = requests.get(url)

#Forking starts here

# Set your GitHub username and personal access token
username = "DhrobePy"
access_token='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'

# Set the API endpoint for forking a repository
api_url = "https://api.github.com/repos/DhrobePy/expenditure/forks"

# Set the owner and repository name for the repository you want to fork
owner = "DhrobePy"
repo = "expenditure"

# Set the forked repository name
forked_repo = "expenditure"

# Set the headers for the API request
headers = {"Authorization": f"Token {access_token}"}

# Set the data for the API request
data = {"organization": username, "name": forked_repo}

# Send the API request to fork the repository
response = requests.post(api_url.format(owner=owner, repo=repo), headers=headers, data=data)

# Check if the fork was successful
if response.status_code == 202:
    print("Repository forked successfully!")
else:
    print("Error forking repository: ", response.text)








#Forking ends here





# Set the URL of the Excel file in the Git repository
file_url = "Expenditure.xlsx"
update_file="extra.xlsx"
#response = requests.get(file_url)
# Read the Excel file into a pandas DataFrame
df = pd.read_excel(file_url)

st.write(df)

#st.set_page_config(page_title="Add Data to Excel Sheet")

# Define a function to add data to the Excel sheet
def add_data_to_excel(date, item_name, quantity):
    # Load the existing Excel file into a Pandas DataFrame
    df = pd.read_excel(file_url)

    # Add a new row to the DataFrame with the given data
    new_row = {"Date": date, "Item Name": item_name, "Quantity": quantity}
    df = df.append(new_row, ignore_index=True)

    # Write the updated DataFrame back to the Excel file
    df.to_excel(update_file, index=False)

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
    df1 = pd.read_excel(file_url)
    st.write(df1)
    
