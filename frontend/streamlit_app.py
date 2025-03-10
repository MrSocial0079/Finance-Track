import streamlit as st
import requests
from components import navbar, transaction_table, spin_wheel, challenges

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Finance Tracker", layout="wide")

# Show Navigation Bar
navbar.show()

# Handle Navigation
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    st.title("🏡 Welcome to Finance Tracker!")
    st.write("Navigate using the sidebar.")

elif st.session_state["page"] == "transactions":
    transaction_table.show(API_URL)

elif st.session_state["page"] == "gamification":
    spin_wheel.show(API_URL)

elif st.session_state["page"] == "challenges":
    challenges.show(API_URL)