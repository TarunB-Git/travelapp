from flask import Flask
from app.core.config import Config
from app.core.extensions import db
from app.features import register_blueprints

def create_app() -> Flask:
    app = Flask("app", template_folder="templates", static_folder="static")

    app.secret_key = "your-very-secret-key"
    app.config.from_object(Config)

    db.init_app(app)
   
    register_blueprints(app)

    return app
