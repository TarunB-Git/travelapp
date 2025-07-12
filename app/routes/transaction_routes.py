from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.transaction import Transaction
from app.models.person import Person
from app.utils.debt_utils import recalculate_debts
from datetime import datetime

transaction_bp = Blueprint("transaction_bp", __name__, url_prefix="/api/transactions")


@transaction_bp.route("", methods=["GET"])
def list_transactions():
    return jsonify([
        {
            "id": t.id,
            "item": t.item_name,
            "cost": t.cost,
            "timestamp": t.timestamp.isoformat(),
            "buyer_id": t.buyer_id,
            "recipients": [r.id for r in t.recipients],
            "budget_category": t.budget_category
        } for t in Transaction.query.all()
    ]), 200

@transaction_bp.route("/add", methods=["POST"])
def add_transaction():
    data = request.get_json() or {}
    req = (data.get("item_name"), data.get("cost"),
           data.get("buyer_id"), data.get("recipient_ids"),
           data.get("budget_category"))
    if any(v is None or (isinstance(v, str) and not v.strip()) for v in req):
        return jsonify({"error": "missing fields"}), 400

    buyer = Person.query.get(data["buyer_id"])
    recipients = Person.query.filter(Person.id.in_(data["recipient_ids"])).all()
    if not buyer or len(recipients) != len(data["recipient_ids"]):
        return jsonify({"error": "invalid people"}), 404

    t = Transaction(
        item_name=data["item_name"].strip(),
        cost=data["cost"],
        timestamp=datetime.utcnow(),
        buyer_id=buyer.id,
        budget_category=data["budget_category"].strip()
    )
    t.recipients.extend(recipients)
    db.session.add(t)
    db.session.commit()

    recalculate_debts()
    return jsonify({"id": t.id}), 201

