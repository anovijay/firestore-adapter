# Application factory for the Firestore adapter service
from flask import Flask, jsonify, send_from_directory, request, current_app
from config import Config, validate_config
from google.cloud import firestore
from google.api_core.exceptions import InvalidArgument, NotFound

# Import the consolidated core functionalities
from core import (
    configure_logging,
    register_error_handlers,
    require_api_key,
    FirestoreClient,
    FilterBuilder,
    AppError
)

def create_app():
    validate_config()
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["ALL_API_KEYS"] = Config.ALL_API_KEYS # Explicitly set for the app context

    # Initialize Firestore client and store on the app
    firestore_client = FirestoreClient(app.config["FIRESTORE_CREDENTIALS"])
    app.extensions["firestore_client"] = firestore_client

    # Register custom error handlers
    register_error_handlers(app)
    
    def get_client():
        """Helper to get the Firestore client from app context."""
        return current_app.extensions["firestore_client"]

    # --- API Routes (moved from routes/documents.py) ---

    @app.route("/")
    def root():
        return jsonify({
            "status": "success",
            "message": "Firestore Adapter service is running.",
            "documentation": "/openapi.yaml"
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "success", "message": "Service is healthy."})

    @app.route('/openapi.yaml')
    def openapi_spec():
        """Serve the OpenAPI specification file."""
        return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')

    @app.route("/documents/<collection>", methods=["GET"])
    @require_api_key
    def query_documents(collection):
        client = get_client()
        db = client.db
        query = db.collection(collection)

        try:
            filters = FilterBuilder.build(request.args)
            for f in filters:
                query = query.where(*f)
        except InvalidArgument as e:
            raise AppError(f"Invalid filter: {e}", 400)

        order_by = request.args.get("order_by")
        if order_by:
            for field in order_by.split(","):
                direction = firestore.Query.DESCENDING if field.startswith("-") else firestore.Query.ASCENDING
                field_name = field.lstrip("-")
                query = query.order_by(field_name, direction=direction)

        try:
            limit = int(request.args.get("limit", 20))
            if not (1 <= limit <= 1000):
                raise AppError("Limit must be between 1 and 1000", 400)
            offset = int(request.args.get("offset", 0))
            if offset < 0:
                raise AppError("Offset must be non-negative", 400)
        except ValueError:
            raise AppError("Limit and offset must be integers", 400)

        query = query.limit(limit)
        docs = list(query.stream())[offset:offset+limit]

        fields = request.args.get("fields")
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
            data = [{k: v for k, v in doc.to_dict().items() if k in field_list} | {"id": doc.id} for doc in docs]
        else:
            data = [{**doc.to_dict(), "id": doc.id} for doc in docs]

        return jsonify({"status": "success", "data": data, "limit": limit, "offset": offset, "count": len(data)})

    @app.route("/documents/<collection>", methods=["POST"])
    @require_api_key
    def create_document(collection):
        data = request.json
        client = get_client()
        
        # Check if a specific doc_id is provided as a query parameter
        doc_id = request.args.get("doc_id")
        
        if doc_id:
            # Create the document with the user-provided ID
            result = client.create_document_with_id(collection, doc_id, data)
        else:
            # Let Firestore generate the ID
            result = client.create_document(collection, data)
            
        return jsonify({"status": "success", "data": result}), 201

    @app.route("/documents/<collection>/<doc_id>", methods=["GET"])
    @require_api_key
    def read_document(collection, doc_id):
        client = get_client()
        doc = client.read_document(collection, doc_id)
        if doc:
            return jsonify({"status": "success", "data": doc})
        raise NotFound("Document not found")

    @app.route("/documents/<collection>/<doc_id>", methods=["PUT"])
    @require_api_key
    def update_document(collection, doc_id):
        data = request.json
        client = get_client()
        try:
            updated = client.update_document(collection, doc_id, data)
            return jsonify({"status": "success", "data": updated})
        except NotFound:
            raise AppError("Document not found", 404)

    @app.route("/documents/<collection>/<doc_id>", methods=["DELETE"])
    @require_api_key
    def delete_document(collection, doc_id):
        client = get_client()
        try:
            result = client.delete_document(collection, doc_id)
            return jsonify({"status": "success", "data": result})
        except NotFound:
            raise AppError("Document not found", 404)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config['DEBUG'], host="0.0.0.0", port=app.config['PORT'])
