# Application factory for the Firestore adapter service
from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import os
from config import Config, validate_config
from utils.errors import register_error_handlers
from utils.logging import configure_logging
from auth import require_api_key
from firestore_client import FirestoreClient
# Insert the parent directory (project root) into sys.path so that "src/" becomes visible.
def create_app():
    validate_config()
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Firestore client once and store on app
    firestore_client = FirestoreClient(app.config["FIRESTORE_CREDENTIALS"])
    app.extensions["firestore_client"] = firestore_client

    from routes.documents import bp as documents_bp
    app.register_blueprint(documents_bp)

    # Serve OpenAPI spec
    @app.route('/openapi.yaml')
    def openapi_spec():
        return send_from_directory(os.path.dirname(__file__), 'openapi.yaml')

    # Swagger UI setup
    swaggerui_bp = get_swaggerui_blueprint('/docs', '/openapi.yaml')
    app.register_blueprint(swaggerui_bp, url_prefix='/docs')

    register_error_handlers(app)

    @app.route("/")
    def root():
        return jsonify({
            "status": "success",
            "message": "Firestore Adapter service is running."
        })

    @app.route("/health")
    def health():
        return jsonify({
            "status": "success",
            "message": "Service is healthy."
        })

    @app.route('/protected')
    @require_api_key
    def protected():
        return {"status": "success"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config['DEBUG'], host="0.0.0.0", port=app.config['PORT'])
