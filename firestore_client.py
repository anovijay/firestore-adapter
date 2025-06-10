from google.cloud import firestore
from google.api_core.exceptions import NotFound
import os
import logging


logger = logging.getLogger(__name__)

class FirestoreClient:
    def __init__(self, credentials_path=None):
        # Credentials path from config, or rely on GOOGLE_APPLICATION_CREDENTIALS env var
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.db = firestore.Client()

    def create_document(self, collection, data):
        """Create a new document and return its contents."""
        try:
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(data)
            logger.info("Created document %s in %s", doc_ref.id, collection)
            return {"id": doc_ref.id, **data}
        except Exception:
            logger.exception("Failed to create document in %s", collection)
            raise

    def create_document_with_id(self, collection, doc_id, data):
        """Create a document using a caller-provided ID."""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.set(data)
            logger.info("Created document %s/%s", collection, doc_id)
            return {"id": doc_id, **data}
        except Exception:
            logger.exception("Failed to create document %s/%s", collection, doc_id)
            raise

    def read_document(self, collection, doc_id):
        """Return a document or None if it does not exist."""
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if doc.exists:
                logger.info("Read document %s/%s", collection, doc_id)
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception:
            logger.exception("Failed to read document %s/%s", collection, doc_id)
            raise

    def update_document(self, collection, doc_id, data):
        """Update an existing document."""
        doc_ref = self.db.collection(collection).document(doc_id)
        try:
            doc_ref.update(data)
            updated_doc = doc_ref.get()
            logger.info("Updated document %s/%s", collection, doc_id)
            return {"id": doc_id, **updated_doc.to_dict()}
        except Exception:
            logger.exception("Failed to update document %s/%s", collection, doc_id)
            raise

    def delete_document(self, collection, doc_id):
        """Delete a document by ID."""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            if not doc_ref.get().exists:
                raise NotFound("Document not found")
            doc_ref.delete()
            logger.info("Deleted document %s/%s", collection, doc_id)
            return {"id": doc_id}
        except Exception:
            logger.exception("Failed to delete document %s/%s", collection, doc_id)
            raise
