from flask import jsonify
from google.api_core.exceptions import NotFound

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({"status": "error", "message": "Resource not found"}), 404

    @app.errorhandler(400)
    def bad_request_error(e):
        return jsonify({"status": "error", "message": "Bad request"}), 400

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    # Optionally, handle Firestore NotFound for any endpoint
    @app.errorhandler(NotFound)
    def firestore_not_found(e):
        return jsonify({"status": "error", "message": "Document not found"}), 404

    # You can add more handlers as needed (e.g., for custom exceptions)
