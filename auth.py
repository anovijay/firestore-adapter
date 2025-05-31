from flask import request, jsonify, current_app

print("LOADING APP.PY")
def require_api_key(view_func):
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        valid_keys = current_app.config["API_KEYS"]
        # Clean empty/blank keys from env
        valid_keys = [k.strip() for k in valid_keys if k.strip()]
        if not api_key or api_key not in valid_keys:
            return jsonify({
                "status": "error",
                "message": "Unauthorized: invalid or missing API key."
            }), 401
        return view_func(*args, **kwargs)
    # Flask's route decorators need __name__ preserved
    wrapper.__name__ = view_func.__name__
    return wrapper
