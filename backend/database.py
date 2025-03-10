import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the path to the service account JSON file
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set")

# Initialize Firestore
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()  # ✅ Fix: Removed the incorrect `database` argument

def get_db():
    return db