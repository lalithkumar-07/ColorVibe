"""
app.py
------
Application factory. Run with:  python app.py
"""

from flask import Flask

from config import Config
from database.db import init_app as init_db
from controllers.main_controller import main_bp
from controllers.auth_controller import auth_bp
from controllers.palette_controller import palette_bp
from controllers.api_controller import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)  # registers the per-request DB connection teardown

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(palette_bp)
    app.register_blueprint(api_bp)

    # Make the logged-in state easy to check in every template.
    @app.context_processor
    def inject_user():
        from flask import session
        return {
            "current_username": session.get("username"),
            "is_logged_in": "user_id" in session,
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
