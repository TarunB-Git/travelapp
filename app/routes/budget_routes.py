from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.budget import Budget
from app.models.person import Person

budget_bp = Blueprint("budget_bp", __name__, url_prefix="/api/budgets")


@budget_bp.route("", methods=["GET"])
def list_budgets():
    return jsonify([
        {"id": b.id, "category": b.category, "daily_limit": b.daily_limit,
         "total_limit": b.total_limit, "person_id": b.person_id}
        for b in Budget.query.all()
    ]), 200

@budget_bp.route("/add", methods=["POST"])
def add_budget():
    data = request.get_json() or {}
    cat = data.get("category", "").strip()
    if not cat:
        return jsonify({"error": "category required"}), 400
    b = Budget(
        category=cat,
        daily_limit=data.get("daily_limit"),
        total_limit=data.get("total_limit")
    )
    db.session.add(b)
    db.session.commit()
    return jsonify({"id": b.id, "category": b.category}), 201

@budget_bp.route("/assign", methods=["POST"])
def assign_budget():
    data = request.get_json() or {}
    b = Budget.query.get(data.get("budget_id"))
    p = Person.query.get(data.get("person_id"))
    if not b or not p:
        return jsonify({"error": "invalid ids"}), 404
    b.person_id = p.id
    db.session.commit()
    return jsonify({"id": b.id, "person_id": p.id}), 200

