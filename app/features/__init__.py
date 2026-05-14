from flask import Flask
from app.features.auth.routes import auth_bp
from app.features.budgets.routes import budget_bp
from app.features.debts.routes import debt_bp
from app.features.exports.routes import export_bp
from app.features.people.routes import person_bp
from app.features.posts.routes import post_bp
from app.features.transactions.routes import transaction_bp
from app.features.ui.routes import views_bp

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
