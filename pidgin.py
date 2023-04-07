import streamlit as st
import pandas as pd
import datetime

# Simple dictionary for storing user information (for demonstration purposes only)
USERS = {
    "user1": {"password": "pass1"},
    "user2": {"password": "pass2"},
}

def dashboard():
    st.title("Dashboard")

    # Create a container for the username and login time
    user_info_container = st.container()

    # Get the current time and format it
    login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add custom CSS to align the username and login time to the right
    user_info_style = """
    <style>
        .user-info {
            position: fixed;
            top: 10px;
            right: 10px;
            text-align: right;
        }
    </style>
    """

    # Display the username and login time using the custom CSS
    user_info_container.markdown(
        f'<div class="user-info">Logged in as: {st.session_state.username}<br>Login Time: {login_time}</div>{user_info_style}',
        unsafe_allow_html=True,
    )

    st.write("Welcome to the dashboard!")
    # Add your dashboard content here

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

    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()
