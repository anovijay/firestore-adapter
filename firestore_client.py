from google.cloud import firestore
from google.api_core.exceptions import NotFound
import os

class FirestoreClient:
    def __init__(self, credentials_path=None):
        # Credentials path from config, or rely on GOOGLE_APPLICATION_CREDENTIALS env var
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.db = firestore.Client()

    def create_document(self, collection, data):
        doc_ref = self.db.collection(collection).document()
        doc_ref.set(data)
        return {"id": doc_ref.id, **data}

    def create_document_with_id(self, collection, doc_id, data):
        """Create a document using a caller-provided ID."""
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.set(data)
        return {"id": doc_id, **data}

    def read_document(self, collection, doc_id):
        doc = self.db.collection(collection).document(doc_id).get()
        if doc.exists:
            return {"id": doc.id, **doc.to_dict()}
        else:
            return None

    def update_document(self, collection, doc_id, data):
        doc_ref = self.db.collection(collection).document(doc_id)
        try:
            doc_ref.update(data)
            updated_doc = doc_ref.get()
            return {"id": doc_id, **updated_doc.to_dict()}
        except Exception as e:
            print(f"Error updating document: {e}")
            return None

    def delete_document(self, collection, doc_id):
        doc_ref = self.db.collection(collection).document(doc_id)
        doc_ref.delete()
        return {"id": doc_id}
