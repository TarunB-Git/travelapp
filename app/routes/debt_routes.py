from flask import Blueprint, jsonify
from app.models.debt import Debt
from sqlalchemy import or_

debt_bp = Blueprint("debt_bp", __name__, url_prefix="/api/debts")


@debt_bp.route("", methods=["GET"])
def list_debts():
    return jsonify([
        {"id": d.id, "lender": d.lender_id, "borrower": d.borrower_id, "amount": d.amount}
        for d in Debt.query.all()
    ]), 200

@debt_bp.route("/<int:pid>", methods=["GET"])
def debts_for(pid):
    ds = Debt.query.filter(or_(Debt.lender_id==pid, Debt.borrower_id==pid)).all()
    return jsonify([
        {"id": d.id, "lender": d.lender_id, "borrower": d.borrower_id, "amount": d.amount}
        for d in ds
    ]), 200

