from flask import Flask
from .person_routes import person_bp
from .budget_routes import budget_bp
from .transaction_routes import transaction_bp
from .debt_routes import debt_bp
from .views import views_bp

def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    for bp in (person_bp, budget_bp, transaction_bp, debt_bp, views_bp):
        app.register_blueprint(bp)

