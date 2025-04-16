import streamlit as st
from pages import login, dashboard, gamification, transactions
from components import navbar
from components import ai_tips
from auth import initialize_firebase, check_authentication

# Initialize Firebase
initialize_firebase()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Check for authentication from URL parameters
check_authentication()

# Show login page if user is not logged in
if not st.session_state.user:
    login.show()
else:
    # Show navbar
    navbar.show()
        # ...
    
    # Show current page
    if st.session_state.current_page == 'dashboard':
        dashboard.show()
    elif st.session_state.current_page == 'gamification':
        gamification.show()
    elif st.session_state.current_page == 'transactions':
        transactions.show()
    elif st.session_state.current_page == 'ai_tips':
        ai_tips.show()
