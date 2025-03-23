import firebase_admin
from firebase_admin import credentials, auth
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin with your service account key
cred = credentials.Certificate("./smart_farming.json")
firebase_admin.initialize_app(cred)

def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return {"success": True, "uid": user.uid}
    except Exception as e:
        return {"success": False, "error": str(e)}


def login_user(email, password):
    # Firebase Admin SDK does not support sign-in directly, so we use Firebase REST API.
    api_key = os.getenv("FIREBASE_API_KEY")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=data)
    return response.json()
