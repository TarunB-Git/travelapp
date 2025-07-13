from flask import Flask
from .person_routes import person_bp
from .budget_routes import budget_bp
from .transaction_routes import transaction_bp
from .export_routes import export_bp
from .debt_routes import debt_bp
from .views import views_bp
from .auth_routes import auth_bp  
from .post_routes import post_bp

def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    for bp in (
        person_bp,
        budget_bp,
        transaction_bp,
        debt_bp,
        export_bp,
        views_bp,
        post_bp,
        auth_bp,  # Register auth routes so /login, /admin/login, etc. work
    ):
        app.register_blueprint(bp)
