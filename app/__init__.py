from flask import Flask
from .config import Config
from .extensions import db, messages_db
from .routes import register_blueprints

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    db.init_app(app)
    messages_db.init_app(app)

    with app.app_context():
        db.create_all()
        messages_db.create_all()

    register_blueprints(app)

    return app


