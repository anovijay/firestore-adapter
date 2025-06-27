from google.cloud import firestore, secretmanager
from google.api_core.exceptions import InvalidArgument, NotFound as GoogleNotFound
from flask import jsonify, current_app, request
from functools import wraps
import os
import sys
import json
import logging
import time

# --- Logging Configuration (from utils/logging.py) ---

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

# --- Error Handling (from utils/errors.py) ---

class AppError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

def handle_app_error(error):
    response = {"status": "error", "message": error.message}
    return jsonify(response), error.status_code

def handle_generic_error(error):
    logging.exception("An unexpected error occurred")
    response = {"status": "error", "message": "Internal Server Error"}
    return jsonify(response), 500

def handle_not_found(error):
    response = {"status": "error", "message": "The requested URL was not found."}
    return jsonify(response), 404

def handle_google_not_found(error):
    """Handle Google's specific NotFound error."""
    return jsonify({"status": "error", "message": str(error)}), 404
    
def register_error_handlers(app):
    app.register_error_handler(AppError, handle_app_error)
    app.register_error_handler(GoogleNotFound, handle_google_not_found)
    app.register_error_handler(Exception, handle_generic_error)
    app.register_error_handler(404, handle_not_found)

# --- API Key Authentication (simplified) ---

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Keys are now loaded directly from the app's config
        valid_keys = current_app.config.get("ALL_API_KEYS", [])
        auth_header = request.headers.get("X-API-KEY")
        
        if not auth_header or auth_header not in valid_keys:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Firestore Client (from firestore_client.py) ---

class FirestoreClient:
    def __init__(self, credentials_path=None):
        if credentials_path and credentials_path.strip():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logging.info("Using explicit credentials from: %s", credentials_path)
        else:
            logging.info("Using default authentication (service account or environment)")
        self.db = firestore.Client()

    def create_document(self, collection, data):
        try:
            doc_ref = self.db.collection(collection).document()
            doc_ref.set(data)
            logging.info("Created document %s in %s", doc_ref.id, collection)
            return {"id": doc_ref.id, **data}
        except Exception as e:
            logging.exception("Failed to create document in %s: %s", collection, e)
            raise AppError("Failed to create document")

    def create_document_with_id(self, collection, doc_id, data):
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.set(data)
            logging.info("Created document %s/%s", collection, doc_id)
            return {"id": doc_id, **data}
        except Exception as e:
            logging.exception("Failed to create document %s/%s: %s", collection, doc_id, e)
            raise AppError("Failed to create document with ID")

    def read_document(self, collection, doc_id):
        try:
            doc = self.db.collection(collection).document(doc_id).get()
            if doc.exists:
                logging.info("Read document %s/%s", collection, doc_id)
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logging.exception("Failed to read document %s/%s: %s", collection, doc_id, e)
            raise AppError("Failed to read document")

    def update_document(self, collection, doc_id, data):
        doc_ref = self.db.collection(collection).document(doc_id)
        try:
            doc_ref.update(data)
            updated_doc = doc_ref.get()
            logging.info("Updated document %s/%s", collection, doc_id)
            return {"id": doc_id, **updated_doc.to_dict()}
        except NotFound:
            raise
        except Exception as e:
            logging.exception("Failed to update document %s/%s: %s", collection, doc_id, e)
            raise AppError("Failed to update document")

    def delete_document(self, collection, doc_id):
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            if not doc_ref.get().exists:
                raise NotFound("Document not found")
            doc_ref.delete()
            logging.info("Deleted document %s/%s", collection, doc_id)
            return {"id": doc_id}
        except NotFound:
            raise
        except Exception as e:
            logging.exception("Failed to delete document %s/%s: %s", collection, doc_id, e)
            raise AppError("Failed to delete document")


# --- Filter Builder (from services/filter_builder.py) ---

class FilterBuilder:
    @staticmethod
    def _auto_type(val: str):
        try:
            if '.' in val: return float(val)
            else: return int(val)
        except (ValueError, TypeError):
            return val

    @staticmethod
    def build(args):
        filters = []
        for key, value in args.items():
            if key in ["limit", "offset", "order_by", "fields", "include_parent"] or key.startswith("subcollection_"):
                continue

            op_map = {
                "_gte": ">=", "_lte": "<=", "_gt": ">", "_lt": "<", "_in": "in"
            }
            
            op = "=="
            field = key
            
            for suffix, operator in op_map.items():
                if key.endswith(suffix):
                    field = key[:-len(suffix)]
                    op = operator
                    break
            
            processed_value = [FilterBuilder._auto_type(v) for v in value.split(',')] if op == "in" else FilterBuilder._auto_type(value)
            filters.append((field, op, processed_value))
            
        return filters 