from flask import jsonify
import uuid
import logging
from google.api_core.exceptions import NotFound

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(e):
        correlation_id = uuid.uuid4().hex
        logger.warning("Not found [%s]", correlation_id)
        return jsonify({"status": "error", "message": "Resource not found", "correlation_id": correlation_id}), 404

    @app.errorhandler(400)
    def bad_request_error(e):
        correlation_id = uuid.uuid4().hex
        logger.warning("Bad request [%s]", correlation_id)
        return jsonify({"status": "error", "message": "Bad request", "correlation_id": correlation_id}), 400

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        correlation_id = uuid.uuid4().hex
        logger.warning("Method not allowed [%s]", correlation_id)
        return jsonify({"status": "error", "message": "Method not allowed", "correlation_id": correlation_id}), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        correlation_id = uuid.uuid4().hex
        logger.exception("Unhandled server error [%s]", correlation_id, exc_info=e)
        return jsonify({"status": "error", "message": "Internal server error", "correlation_id": correlation_id}), 500

    # Optionally, handle Firestore NotFound for any endpoint
    @app.errorhandler(NotFound)
    def firestore_not_found(e):
        correlation_id = uuid.uuid4().hex
        logger.warning("Document not found [%s]", correlation_id)
        return jsonify({"status": "error", "message": "Document not found", "correlation_id": correlation_id}), 404

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        correlation_id = uuid.uuid4().hex
        logger.exception("Unhandled exception [%s]", correlation_id, exc_info=e)
        return jsonify({"status": "error", "message": "Internal server error", "correlation_id": correlation_id}), 500

    # You can add more handlers as needed (e.g., for custom exceptions)
