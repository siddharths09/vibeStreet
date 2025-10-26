import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CRED_PATH
import re

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def sanitize_document_id(neighborhood):
    """
    Sanitize neighborhood name for use as Firestore document ID
    Replace problematic characters with safe alternatives
    """
    # Replace forward slashes with underscores
    sanitized = neighborhood.replace('/', '_')
    # Remove any other problematic characters
    sanitized = re.sub(r'[^\w\s-]', '', sanitized)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized

def save_neighborhood_data(db, neighborhood, data):
    """Save neighborhood data to Firebase"""
    doc_id = sanitize_document_id(neighborhood)
    doc_ref = db.collection('neighborhoods').document(doc_id)
    
    # Ensure the original neighborhood name is in the data
    data['neighborhood'] = neighborhood
    data['doc_id'] = doc_id
    
    doc_ref.set(data, merge=True)
    print(f"✅ Saved data for {neighborhood} (ID: {doc_id})")

def get_all_neighborhoods(db):
    """Retrieve all neighborhood data"""
    docs = db.collection('neighborhoods').stream()
    return {doc.id: doc.to_dict() for doc in docs}

def get_neighborhood_by_name(db, neighborhood):
    """Get a specific neighborhood by its original name"""
    doc_id = sanitize_document_id(neighborhood)
    doc_ref = db.collection('neighborhoods').document(doc_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None