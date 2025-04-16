import streamlit as st
import os
import requests
import json
from typing import Optional
from pathlib import Path

# Firebase configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyCGBMgzkR5U7qjkSDg30nxv7NZ3rz7yaSQ",
    "authDomain": "finunity.firebaseapp.com",
    "projectId": "finunity",
    "storageBucket": "finunity.firebasestorage.app",
    "messagingSenderId": "487174554613",
    "appId": "1:487174554613:web:ec28ace44eccafee67d6bc",
    "measurementId": "G-7B86W7ERFG"
}

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def initialize_firebase():
    """Initialize Firebase in the browser"""
    # Try to load config from file if available
    try:
        config_path = Path(__file__).parent / 'firebase_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = FIREBASE_CONFIG
    except Exception as e:
        st.warning(f"Error loading Firebase config: {e}")
        config = FIREBASE_CONFIG
        
    firebase_script = f"""
    <script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.8.1/firebase-auth-compat.js"></script>
    <script>
    const firebaseConfig = {json.dumps(config)};
    
    // Store config in localStorage for other components to use
    localStorage.setItem('firebaseConfig', JSON.stringify(firebaseConfig));
    
    // Initialize Firebase if not already initialized
    if (!firebase.apps || !firebase.apps.length) {{
        firebase.initializeApp(firebaseConfig);
    }}

    const auth = firebase.auth();
    </script>
    
    <div id="error-message" style="display: none; color: red; margin: 10px 0;"></div>
    <div id="success-message" style="display: none; color: green; margin: 10px 0;"></div>
    """
    st.markdown(firebase_script, unsafe_allow_html=True)

def verify_token(token: str) -> Optional[dict]:
    """Verify Firebase token with backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None

def check_authentication():
    """Check if user is authenticated"""
    token = st.query_params.get('token')
    if token:
        user_data = verify_token(token)
        if user_data:
            st.session_state.user = {
                'uid': user_data['uid'],
                'email': user_data['email'],
                'name': user_data.get('name', '')
            }
            st.session_state.auth_token = token
            st.query_params.clear()
            return True
    
    return False

def login_form():
    """Email login form"""
    initialize_firebase()
    
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit and email and password:
            with st.spinner("Logging in..."):
                result = authenticate_user(email, password)
                if result["success"]:
                    st.success("Login successful!")
                    st.session_state.user = result["user"]
                    st.session_state.auth_token = result["token"]
                    st.rerun()
                else:
                    st.error(result["message"])



def signup_form():
    """User signup form"""
    initialize_firebase()
    
    with st.form("signup"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            if not all([name, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                # Call backend directly instead of using JavaScript
                with st.spinner("Creating account..."):
                    result = create_user(email, password, name)
                    if result["success"]:
                        # Explicitly ignore any token or user data returned
                        # Do not set any session state for user or token
                        st.success("Account created successfully! Please log in with your credentials.")
                        # Switch to login tab (index 0)
                        st.session_state.active_tab = 0
                        # Force a rerun to ensure we're on the login tab
                        st.rerun()
                    else:
                        st.error(result["message"])



def auth_page():
    """Main authentication page"""
    if not check_authentication():
        st.title("Welcome to Fintrack")
        
        # Initialize active_tab if not set
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = 0
            
        # Create tabs
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        # Show the appropriate form based on the active tab
        if st.session_state.active_tab == 0:
            with tab1:
                login_form()
        else:
            with tab2:
                signup_form()
    else:
        st.success("You are logged in!")

def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user with email and password"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signin",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "user": {
                    "uid": data.get("uid", ""),
                    "email": data.get("email", ""),
                    "name": data.get("name", "")
                },
                "token": data.get("token", "")
            }
        else:
            error_msg = "Invalid credentials"
            if response.status_code != 401:  # If not just unauthorized
                try:
                    error_msg = response.json().get("detail", error_msg)
                except:
                    pass
            return {"success": False, "message": error_msg}
    except requests.RequestException as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}

def create_user(email: str, password: str, name: str = "") -> dict:
    """Create a new user account"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={"email": email, "password": password, "name": name}
        )
        
        if response.status_code == 200:
            data = response.json()
            # Add JavaScript to check for verification email status
            st.markdown(
                """
                <script>
                // Initialize Firebase if needed
                if (typeof firebase === 'undefined') {
                    // Load Firebase scripts dynamically
                    const firebaseApp = document.createElement('script');
                    firebaseApp.src = 'https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js';
                    document.head.appendChild(firebaseApp);
                    
                    const firebaseAuth = document.createElement('script');
                    firebaseAuth.src = 'https://www.gstatic.com/firebasejs/10.8.1/firebase-auth-compat.js';
                    document.head.appendChild(firebaseAuth);
                    
                    // Initialize after scripts load
                    firebaseAuth.onload = () => {
                        const firebaseConfig = JSON.parse(localStorage.getItem('firebaseConfig'));
                        if (firebaseConfig) {
                            firebase.initializeApp(firebaseConfig);
                        }
                    };
                }
                </script>
                """,
                unsafe_allow_html=True
            )
            
            return {
                "success": True,
                "user": {
                    "uid": data.get("uid", ""),
                    "email": data.get("email", ""),
                    "name": data.get("name", "")
                },
                "token": data.get("token", "")
            }
        else:
            error_msg = "Failed to create account"
            try:
                error_msg = response.json().get("detail", error_msg)
            except:
                pass
            return {"success": False, "message": error_msg}
    except requests.RequestException as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}



if __name__ == "__main__":
    auth_page()