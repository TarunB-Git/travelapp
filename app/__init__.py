from flask import Flask
from .config import Config
from .extensions import db, messages_db
from .routes import register_blueprints

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")

    app.secret_key = 'your-very-secret-key' 
    app.config.from_object(Config)

    db.init_app(app)
   
    register_blueprints(app)

    return app


