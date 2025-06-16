from flask import Blueprint, request, jsonify, current_app
from auth import require_api_key
from services.filter_builder import FilterBuilder
from google.cloud import firestore
from google.api_core.exceptions import InvalidArgument, NotFound

bp = Blueprint("documents", __name__)

def get_client():
    return current_app.extensions["firestore_client"]

@bp.route("/documents/<collection>", methods=["GET"])
@require_api_key
def query_documents(collection):
    client = get_client()
    db = client.db
    query = db.collection(collection)

    # ---- 1. Build Filters ----
    filters = FilterBuilder.build(request.args)
    # Apply filters to Firestore query
    try:
        for f in filters:
            query = query.where(*f)
    except InvalidArgument as e:
        return jsonify({"status": "error", "message": f"Invalid filter: {e}"}), 400

    # ---- 2. Sorting (order_by) ----
    order_by = request.args.get("order_by")
    if order_by:
        for field in order_by.split(","):
            direction = firestore.Query.DESCENDING if field.startswith("-") else firestore.Query.ASCENDING
            field_name = field.lstrip("-")
            query = query.order_by(field_name, direction=direction)

    # ---- 3. Pagination ----
    try:
        limit = int(request.args.get("limit", 20))
        if limit < 1 or limit > 1000:
            return jsonify({"status": "error", "message": "Limit must be between 1 and 1000"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Limit must be an integer"}), 400

    try:
        offset = int(request.args.get("offset", 0))
        if offset < 0:
            return jsonify({"status": "error", "message": "Offset must be >= 0"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Offset must be an integer"}), 400

    query = query.limit(limit)
    docs = query.stream()
    docs = list(docs)[offset:offset+limit]

    # ---- 4. Field Selection ----
    fields = request.args.get("fields")
    if fields:
        field_list = [f.strip() for f in fields.split(",")]
        data = [{k: v for k, v in doc.to_dict().items() if k in field_list} | {"id": doc.id} for doc in docs]
    else:
        data = [{**doc.to_dict(), "id": doc.id} for doc in docs]

    # ---- 5. Response ----
    return jsonify({
        "status": "success",
        "data": data,
        "limit": limit,
        "offset": offset,
        "count": len(data)
    })

@bp.route("/documents/<collection>", methods=["POST"])
@require_api_key
def create_document(collection):
    data = request.json
    client = get_client()
    result = client.create_document(collection, data)
    return jsonify({"status": "success", "data": result})

@bp.route("/documents/<collection>/<doc_id>", methods=["GET"])
@require_api_key
def read_document(collection, doc_id):
    client = get_client()
    doc = client.read_document(collection, doc_id)
    if doc:
        return jsonify({"status": "success", "data": doc})
    else:
        return jsonify({"status": "error", "message": "Not found"}), 404

@bp.route("/documents/<collection>/<doc_id>", methods=["POST"])
@require_api_key
def create_document_with_id(collection, doc_id):
    data = request.json
    client = get_client()
    result = client.create_document_with_id(collection, doc_id, data)
    return jsonify({"status": "success", "data": result}), 201

@bp.route("/documents/<collection>/<doc_id>", methods=["PUT"])
@require_api_key
def update_document(collection, doc_id):
    data = request.json
    client = get_client()
    try:
        updated = client.update_document(collection, doc_id, data)
        return jsonify({"status": "success", "data": updated})
    except NotFound:
        return jsonify({"status": "error", "message": "Document not found"}), 404

@bp.route("/documents/<collection>/<doc_id>", methods=["DELETE"])
@require_api_key
def delete_document(collection, doc_id):
    client = get_client()
    try:
        result = client.delete_document(collection, doc_id)
        return jsonify({"status": "success", "data": result})
    except NotFound:
        return jsonify({"status": "error", "message": "Document not found"}), 404

@bp.route("/collections/<collection>/subcollections/<subcollection>", methods=["GET"])
@require_api_key
def query_collection_with_subcollection(collection, subcollection):
    """
    Query all documents in a collection along with their subcollection documents.
    Supports filtering on both collection and subcollection fields.
    
    Query parameters:
    - collection_*: Filters for the main collection (e.g., collection_status=active)
    - subcollection_*: Filters for the subcollection (e.g., subcollection_type=pdf)
    - Standard filter operators: _gte, _lte, _gt, _lt, _in, or == (default)
    """
    client = get_client()
    
    try:
        # Separate collection and subcollection filters from query parameters
        collection_params = {}
        subcollection_params = {}
        
        for key, value in request.args.items():
            if key.startswith("collection_"):
                # Remove the "collection_" prefix
                field_name = key[11:]  # len("collection_") = 11
                collection_params[field_name] = value
            elif key.startswith("subcollection_"):
                # Remove the "subcollection_" prefix  
                field_name = key[14:]  # len("subcollection_") = 14
                subcollection_params[field_name] = value
        
        # Build filters using the existing FilterBuilder
        collection_filters = FilterBuilder.build(collection_params) if collection_params else None
        subcollection_filters = FilterBuilder.build(subcollection_params) if subcollection_params else None
        
        # Query the collection with subcollection
        results = client.query_collection_with_subcollection(
            collection_name=collection,
            subcollection_name=subcollection,
            collection_filters=collection_filters,
            subcollection_filters=subcollection_filters
        )
        
        return jsonify({
            "status": "success",
            "data": results,
            "count": len(results),
            "collection": collection,
            "subcollection": subcollection
        })
        
    except InvalidArgument as e:
        return jsonify({"status": "error", "message": f"Invalid filter: {e}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Query failed: {str(e)}"}), 500
