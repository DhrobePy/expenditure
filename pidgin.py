import streamlit as st
import pandas as pd
import requests
#response = requests.get(url)

# Set the URL of the Excel file in the Git repository
file_url = "https://github.com/DhrobePy/expenditure/blob/a5ff7a45e75f73522f84539bf153f3210c2112cb/Expenditure.xlsx?raw=true"

#response = requests.get(file_url)
# Read the Excel file into a pandas DataFrame
df = pd.read_excel(file_url)

st.write(df)
