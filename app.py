from flask import Flask, render_template, request, redirect, url_for, session, flash
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    if 'user' in session:
        logger.debug(f"User in session: {session['user']}")
        # Get user data from Firestore
        user_doc = db.collection('users').document(session['user']['uid']).get()
        user_data = user_doc.to_dict() if user_doc.exists else None
        logger.debug(f"User data from Firestore: {user_data}")
        return render_template('dashboard.html', user=session['user'], user_data=user_data)
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Sign in with Firebase
            user = auth.get_user_by_email(email)
            logger.debug(f"User found in Firebase Auth: {user.uid}")
            
            # Get user data from Firestore
            user_doc = db.collection('users').document(user.uid).get()
            if user_doc.exists:
                logger.debug(f"User data from Firestore: {user_doc.to_dict()}")
            
            session['user'] = {
                'email': email,
                'uid': user.uid
            }
            return redirect(url_for('home'))
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('Invalid credentials')
            return redirect(url_for('login'))
    
    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True) 