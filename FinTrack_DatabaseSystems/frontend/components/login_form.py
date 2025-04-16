import streamlit as st

def login_form():
    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # For now, just show success message
            st.success("🎉 Login successful!")
            st.session_state.user = {"email": email}  # Store user in session state
            st.rerun()  # Rerun to update the UI

def signup_form():
    with st.form("signup_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif len(password) < 6:
                st.error("❌ Password should be at least 6 characters long!")
            else:
                st.success("✅ Account created successfully! Please login.")
