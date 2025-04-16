import streamlit as st
import os
import requests
import json
from auth import authenticate_user, create_user

def get_firebase_config():
    """
    Retrieve Firebase configuration from environment variables or .env file
    """
    try:
        # Attempt to load from environment variables
        config = {
            "apiKey": os.getenv("AIzaSyCGBMgzkR5U7qjkSDg30nxv7NZ3rz7yaSQ"),
            "authDomain": os.getenv("finunity.firebaseapp.com"),
            "projectId": os.getenv("finunity")
        }
        
        # Validate configuration
        if not all(config.values()):
            # Fallback to loading from a config file if env vars are not set
            config_path = os.path.join(os.path.dirname(__file__), '..', 'firebase_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
        
        return config
    except Exception as e:
        st.error(f"Error loading Firebase configuration: {e}")
        return None

def render_google_login_script():
    """
    Dynamically generate Firebase Google Sign-In script
    """
    config = get_firebase_config()
    if not config:
        st.error("Firebase configuration could not be loaded")
        return
    
    # Generate Firebase initialization script
    firebase_script = f"""
    <script src="[https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js"></script>](https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js"></script>)
    <script src="[https://www.gstatic.com/firebasejs/10.8.1/firebase-auth-compat.js"></script>](https://www.gstatic.com/firebasejs/10.8.1/firebase-auth-compat.js"></script>)
    <script>
    const firebaseConfig = {{
        apiKey: "{config['apiKey']}",
        authDomain: "{config['authDomain']}",
        projectId: "{config['projectId']}"
    }};

    firebase.initializeApp(firebaseConfig);

    const auth = firebase.auth();

    function googleSignIn() {{
        const provider = new firebase.auth.GoogleAuthProvider();
        auth.signInWithPopup(provider)
            .then(result => {{
                return result.user.getIdToken();
            }})
            .then(idToken => {{
                // Redirect to Streamlit with token
                window.location.href = `http://localhost:8501/?token=${{idToken}}`;
            }})
            .catch(error => {{
                alert("Login Failed: " + error.message);
            }});
    }}
    </script>
    """
    
    # Use st.markdown to inject the script
    st.markdown(firebase_script, unsafe_allow_html=True)
    
    # Add Google Sign-In button
    st.markdown("""
    <button onclick="googleSignIn()" style="
        width: 100%; 
        padding: 10px; 
        background-color: #4285F4; 
        color: white; 
        border: none; 
        border-radius: 4px; 
        cursor: pointer;
    ">
        <img src="[https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google-logo.svg"](https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google-logo.svg") 
             style="vertical-align: middle; margin-right: 10px; height: 20px;">
        Sign in with Google
    </button>
    """, unsafe_allow_html=True)

def login_page():
    """
    Streamlit login page with Google Sign-In
    """
    st.title("Welcome to Fintrack")

    
    # Create two columns for login methods
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Google Sign-In")
        render_google_login_script()
    
    with col2:
        st.subheader("Email Login")
        with st.form("email_login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                # Implement email login logic here
                pass

    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #666;">
        <p>Track your finances with AI-powered insights 🚀</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    if 'user' not in st.session_state:
        login_page()
    else:
        # Redirect to main app or dashboard
        st.write(f"Welcome, {st.session_state.user['name']}")

# Optional: Add Google Sign-In token verification
def google_signin():
    """
    Handle Google Sign-In in Streamlit
    """
    # Check if token is in query params
    token = st.query_params.get('token')
    
    if token:
        try:
            # Send token to backend for verification
            response = requests.post(
                f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/google-signin", 
                json={"id_token": token}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Store user info in session state
                st.session_state.user = {
                    'uid': user_data['uid'],
                    'email': user_data['email'],
                    'name': user_data.get('name', ''),
                    'picture': user_data.get('picture', '')
                }
                
                # Store authentication token
                st.session_state.auth_token = user_data['token']
                
                # Clear the token from URL to prevent reuse
                st.query_params.clear()
                
                st.success("Google Sign-In successful!")
                return True
            else:
                st.error("Authentication failed")
                return False
        
        except requests.RequestException as e:
            st.error(f"Network error: {e}")
            return False
    
    return False

def show():
    """Main function to display the login page"""
    st.title("Welcome to Fintrack")
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    # Login Tab
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if email and password:
                    with st.spinner("Logging in..."):
                        result = authenticate_user(email, password)
                        if result["success"]:
                            st.session_state.user = result["user"]
                            st.session_state.auth_token = result["token"]
                            st.rerun()
                        else:
                            st.error(result["message"])
                else:
                    st.error("Please enter both email and password")
    
    # Sign Up Tab
    with tab2:
        with st.form("signup_form"):
            new_name = st.text_input("Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Sign Up")
            
            if signup_button:
                if new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        with st.spinner("Creating account..."):
                            result = create_user(new_email, new_password, new_name)
                            if result["success"]:
                                st.success("Account created successfully! You can now log in.")
                                # Auto-login after signup
                                st.session_state.user = result["user"]
                                st.session_state.auth_token = result["token"]
                                st.rerun()
                            else:
                                st.error(result["message"])
                else:
                    st.error("Please fill in all fields")
    

    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #666;">
        <p>Track your finances with AI-powered insights 🚀</p>
    </div>
    """, unsafe_allow_html=True)