from flask import Blueprint, Response
from io import StringIO
import csv
from app.models import Budget, Transaction

export_bp = Blueprint("export_bp", __name__)

@export_bp.route("/export/transactions.csv")
def export_transactions():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Timestamp", "Item", "Cost", "Buyer", "Category", "Recipients"])
    for t in Transaction.query.all():
        writer.writerow([
            t.timestamp.strftime("%Y-%m-%d %H:%M"),
            t.item_name,
            t.cost,
            t.buyer.name,
            t.budget_category,
            ", ".join(r.name for r in t.recipients)
        ])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=transactions.csv"})

@export_bp.route("/export/budgets.csv")
def export_budgets():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Category", "Daily Limit", "Total Limit", "People"])
    for b in Budget.query.all():
        writer.writerow([
            b.category,
            b.daily_limit or "",
            b.total_limit or "",
            ", ".join(p.name for p in b.people)
        ])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=budgets.csv"})