from flask import Flask, jsonify
from config import Config
from utils.errors import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from routes.documents import bp as documents_bp
    app.register_blueprint(documents_bp)

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

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config['DEBUG'], host="0.0.0.0", port=app.config['PORT'])
