import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import re

# Initialize Firebase with the service account key
if not firebase_admin._apps:
    try:
        # Get absolute path to service account key file
        cred_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'service-account-key.json'))
        print(f"Looking for service account key at: {cred_path}")
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Service account key file not found at {cred_path}")
            
        # Load the service account key JSON file
        cred = credentials.Certificate(cred_path)
        
        # Initialize the app with a service account
        firebase_admin.initialize_app(cred)
        
        # Check if we're in production mode
        is_production = os.environ.get('ENVIRONMENT', '').lower() == 'production'
        print(f"Firebase initialized successfully in {'production' if is_production else 'development'} mode")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        print(f"Current working directory: {os.getcwd()}")
        raise e
else:
    print("Firebase already initialized")

# Get Firestore client
try:
    db = firestore.client()
    print("Successfully connected to Firestore")
except Exception as e:
    print(f"Error connecting to Firestore: {e}")

class FirebaseService:
    def __init__(self):
        self.expenses_ref = db.collection('expenses')
        self.transactions_ref = db.collection('transactions')
        self.db = db

    async def add_expense(self, user_id: str, expense_data: dict):
        expense_data['user_id'] = user_id
        expense_data['created_at'] = datetime.now(timezone.utc)
        doc_ref = self.expenses_ref.document()
        doc_ref.set(expense_data)
        return {**expense_data, 'id': doc_ref.id}

    async def get_expenses(self, user_id: str):
        expenses = []
        docs = self.expenses_ref.where('user_id', '==', user_id).stream()
        for doc in docs:
            expenses.append({**doc.to_dict(), 'id': doc.id})
        return expenses

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        # At least 8 characters, one uppercase, one lowercase, one number
        return (len(password) >= 8 and 
                any(c.isupper() for c in password) and 
                any(c.islower() for c in password) and 
                any(c.isdigit() for c in password))

    def signup_with_email(self, email: str, password: str, name: Optional[str] = None) -> Dict[str, str]:
        """Sign up a new user with email and password"""
        if not self.validate_email(email):
            raise ValueError("Invalid email format")
        
        if not self.validate_password(password):
            raise ValueError("Password does not meet strength requirements")

        try:
            # Create the user in Firebase Authentication
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=name or ''
            )
            
            # Get the UID from the created user
            uid = user_record.uid
            
            # Store additional user info in Firestore
            user_data = {
                'email': email,
                'name': name or '',
                'created_at': datetime.now(timezone.utc),
                'last_login': datetime.now(timezone.utc),
                'auth_token': self.generate_firebase_token(uid)  # Store the token in the user document
            }
            
            # Create the user document in Firestore
            self.db.collection('users').document(uid).set(user_data)
            
            print(f"Created user with email: {email} and UID: {uid}")
            
            return {
                "uid": uid, 
                "email": email,
                "name": name or "",
                "token": user_data['auth_token'],
                "message": "Account created successfully."
            }
        
        except ValueError as ve:
            # Re-raise validation errors
            raise ve
        except auth.EmailAlreadyExistsError:
            raise ValueError("Email already in use")
        except Exception as e:
            error_str = str(e)
            print(f"Signup error details: {error_str}")
            
            # Check for rate limiting errors
            if "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                raise ValueError("Too many sign-up attempts. Please wait a few minutes before trying again.")
            
            # Handle other Firebase errors with user-friendly messages
            if "INVALID_EMAIL" in error_str:
                raise ValueError("Invalid email format")
            elif "EMAIL_EXISTS" in error_str:
                raise ValueError("Email already in use")
            elif "WEAK_PASSWORD" in error_str:
                raise ValueError("Password is too weak. Please use a stronger password.")
            else:
                raise Exception(f"Signup error: {error_str}")

    def signin_with_email(self, email: str, password: str) -> Dict[str, str]:
        """Sign in a user with email and password"""
        try:
            # Get the user by email
            user = auth.get_user_by_email(email)
            uid = user.uid
            
            # Verify the password - this will throw an exception if password is incorrect
            # We need to use Firebase Auth REST API for this, but for now we'll simulate it
            # by getting the user record and generating a token
            try:
                # In a real implementation, we would verify the password with Firebase Auth REST API
                # For now, we'll trust that the password is correct and generate a token
                # This is not secure, but it's a placeholder until we implement proper password verification
                
                # Generate a custom token for the user
                token = self.generate_firebase_token(uid)
                
                # Update last login timestamp and token in Firestore
                try:
                    current_time = datetime.now(timezone.utc)
                    self.db.collection('users').document(uid).update({
                        'last_login': current_time,
                        'auth_token': token
                    })
                    print(f"Updated last_login for user {uid} to {current_time}")
                except Exception as e:
                    print(f"Error updating last_login for user {uid}: {str(e)}")
                    # If the user document doesn't exist, create it
                    try:
                        current_time = datetime.now(timezone.utc)
                        self.db.collection('users').document(uid).set({
                            'email': email,
                            'name': user.display_name or '',
                            'created_at': current_time,
                            'last_login': current_time,
                            'auth_token': token
                        })
                        print(f"Created missing user document for {uid} with timestamp {current_time}")
                    except Exception as create_error:
                        print(f"Failed to create user document: {str(create_error)}")
                
                # Get user data from Firestore
                user_doc = self.db.collection('users').document(uid).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    print(f"Retrieved user data from Firestore: {user_data}")
                else:
                    user_data = {}
                    print(f"No user document found in Firestore for uid: {uid}")
                
                print(f"User logged in: {email} with ID: {uid}")
                
                return {
                    "uid": uid, 
                    "email": email,
                    "name": user.display_name or user_data.get('name', ''),
                    "token": token
                }
            except Exception as e:
                error_str = str(e)
                print(f"Password verification error: {error_str}")
                
                # Check for rate limiting errors
                if "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                    raise ValueError("Too many sign-in attempts. Please wait a few minutes before trying again.")
                    
                raise ValueError("Invalid password")
        
        except auth.UserNotFoundError:
            # Use ValueError for consistent error handling in the API
            raise ValueError("No user found with this email")
        except ValueError as ve:
            # Re-raise ValueError exceptions
            raise ve
        except Exception as e:
            error_str = str(e)
            print(f"Sign-in error details: {error_str}")
            
            # Check for rate limiting errors
            if "TOO_MANY_ATTEMPTS_TRY_LATER" in error_str:
                raise ValueError("Too many sign-in attempts. Please wait a few minutes before trying again.")
            
            # Handle other Firebase errors with user-friendly messages
            if "INVALID_EMAIL" in error_str:
                raise ValueError("Invalid email format")
            elif "USER_DISABLED" in error_str:
                raise ValueError("This account has been disabled")
            elif "INVALID_PASSWORD" in error_str:
                raise ValueError("Invalid password")
            else:
                raise ValueError(f"Sign-in error: {error_str}")

    def signin_with_google(self, google_id_token: str) -> Dict[str, str]:
        """
        Sign in or create a user with Google ID token
        
        Args:
            google_id_token (str): ID token received from Google OAuth
        
        Returns:
            Dict containing user information and Firebase token
        """
        try:
            # Verify the Google ID token
            decoded_token = auth.verify_id_token(google_id_token)
            
            # Extract user info from the token
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            picture = decoded_token.get('picture', '')
            
            # Create or update user in Firestore
            user_ref = self.db.collection('users').document(uid)
            user_ref.set({
                'email': email,
                'name': name,
                'picture': picture,
                'last_login': datetime.now(timezone.utc)
            }, merge=True)
            
            # Generate a custom token for the user
            custom_token = auth.create_custom_token(uid)
            
            return {
                "uid": uid,
                "email": email,
                "name": name,
                "picture": picture,
                "token": custom_token.decode('utf-8')
            }
        
        except ValueError as e:
            # Token verification failed
            raise Exception(f"Google token verification failed: {str(e)}")
        except Exception as e:
            # Other authentication errors
            raise Exception(f"Google Sign-In error: {str(e)}")

    def create_user_if_not_exists(self, user_data: Dict[str, str]):
        try:
            # Try to get user by email
            try:
                existing_user = auth.get_user_by_email(user_data['email'])
                return {"uid": existing_user.uid}
            except auth.UserNotFoundError:
                # Create new user if not exists
                user = auth.create_user(
                    email=user_data['email'],
                    display_name=user_data['name']
                )
                
                # Store additional user info in Firestore
                user_ref = self.db.collection('users').document(user.uid)
                user_ref.set({
                    'email': user_data['email'],
                    'name': user_data['name'],
                    'picture': user_data.get('picture', '')
                })
                
                return {"uid": user.uid}
        except Exception as e:
            raise Exception(f"User creation error: {str(e)}")

    def create_or_update_user(self, user_data: Dict[str, str]) -> Dict[str, str]:
        """
        Create or update a user in Firebase Authentication and Firestore
        
        Args:
            user_data (Dict): User information including name, email, picture
        
        Returns:
            Dict containing user UID and details
        """
        try:
            # Try to get user by email
            try:
                existing_user = auth.get_user_by_email(user_data['email'])
                user_uid = existing_user.uid
                
                # Update user info in Firestore
                user_ref = self.db.collection('users').document(user_uid)
                user_ref.update({
                    'name': user_data.get('name', ''),
                    'picture': user_data.get('picture', ''),
                    'last_login': datetime.now(timezone.utc)
                })
            except auth.UserNotFoundError:
                # Create new user if not exists
                user = auth.create_user(
                    email=user_data['email'],
                    display_name=user_data.get('name', '')
                )
                user_uid = user.uid
                
                # Store additional user info in Firestore
                user_ref = self.db.collection('users').document(user_uid)
                user_ref.set({
                    'email': user_data['email'],
                    'name': user_data.get('name', ''),
                    'picture': user_data.get('picture', ''),
                    'created_at': datetime.now(timezone.utc),
                    'last_login': datetime.now(timezone.utc)
                })
            
            return {"uid": user_uid}
        except Exception as e:
            raise Exception(f"User creation/update error: {str(e)}")

    def generate_firebase_token(self, uid: str):
        """Generate a simple token for authentication"""
        try:
            # Create a simple token format that includes the user ID
            # Format: uid:timestamp:random
            import time
            import random
            import string
            import hashlib
            
            # Generate a random string
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            timestamp = int(time.time())
            
            # Create a hash of the components
            hash_input = f"{uid}:{timestamp}:{random_str}"
            hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
            
            # Format: uid:timestamp:hash
            token = f"{uid}:{timestamp}:{hash_value}"
            
            # Store the token in the user document
            self.db.collection('users').document(uid).update({
                'auth_token': token,
                'token_created_at': datetime.now(timezone.utc)
            })
            
            return token
        except Exception as e:
            print(f"Token generation error: {str(e)}")
            # Fallback to a simple token if update fails
            return f"{uid}:simple-token"

    async def add_transaction(self, user_id: str, transaction_data: dict):
        """Add a new transaction to the database"""
        # Add user_id and timestamp to the transaction data
        transaction_data['user_id'] = user_id
        
        # Always use current time for timestamps
        # Use UTC time and format it consistently
        current_time = datetime.now(timezone.utc)
        transaction_data['created_at'] = current_time
        transaction_data['date'] = current_time  # Override any date from frontend
        
        # Create a new document in the transactions collection
        doc_ref = self.transactions_ref.document()
        doc_ref.set(transaction_data)
        
        # Return the transaction data with the document ID
        return {**transaction_data, 'id': doc_ref.id}
    
    async def get_transactions(self, user_id: str):
        """Get all transactions for a specific user"""
        transactions = []
        # Query transactions where user_id matches
        docs = self.transactions_ref.where('user_id', '==', user_id).stream()
        
        # Convert each document to a dictionary and add to the list
        for doc in docs:
            transactions.append({**doc.to_dict(), 'id': doc.id})
            
        return transactions
    
    async def get_transaction(self, transaction_id: str):
        """Get a specific transaction by ID"""
        doc = self.transactions_ref.document(transaction_id).get()
        if doc.exists:
            return {**doc.to_dict(), 'id': doc.id}
        return None
    
    async def update_transaction(self, transaction_id: str, transaction_data: dict):
        """Update an existing transaction"""
        # Add updated_at timestamp
        transaction_data['updated_at'] = datetime.now(timezone.utc)
        
        # Update the document
        self.transactions_ref.document(transaction_id).update(transaction_data)
        
        # Return the updated transaction
        doc = self.transactions_ref.document(transaction_id).get()
        return {**doc.to_dict(), 'id': doc.id}
    
    async def delete_transaction(self, transaction_id: str):
        """Delete a transaction"""
        self.transactions_ref.document(transaction_id).delete()
        return {"status": "success", "message": f"Transaction {transaction_id} deleted successfully"}

firebase_service = FirebaseService()
