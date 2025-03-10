import streamlit as st

def show():
    st.sidebar.title("Navigation")

    # Navigation options
    page = st.sidebar.radio("Go to", ["Home", "Transactions", "Spin the Wheel", "Challenges"])

    # Redirect based on selection
    if page == "Home":
        st.session_state["page"] = "home"
    elif page == "Transactions":
        st.session_state["page"] = "transactions"
    elif page == "Spin the Wheel":
        st.session_state["page"] = "gamification"
    elif page == "Challenges":
        st.session_state["page"] = "challenges"