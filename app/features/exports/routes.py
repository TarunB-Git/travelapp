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

@export_bp.route("/export/budget-stats.csv")
def export_budget_stats():
    from collections import defaultdict
    from datetime import date
    from app.models import Person, Budget, Transaction

    today = date.today()
    people = Person.query.all()
    budgets = Budget.query.all()
    txns = Transaction.query.all()

    spend_map = defaultdict(lambda: defaultdict(float))

    for txn in txns:
        if txn.timestamp.date() != today or not txn.recipients:
            continue
        share = txn.cost / len(txn.recipients)
        for rec in txn.recipients:
            spend_map[rec.id][txn.budget_category] += share

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Person", "Category", "Spent", "Limit", "Remaining"])

    for person in people:
        for b in budgets:
            if person not in b.people:
                continue
            spent = round(spend_map[person.id].get(b.category, 0), 2)
            limit = b.daily_limit or 0
            remaining = round(max(limit - spent, 0), 2)
            writer.writerow([person.name, b.category, spent, limit, remaining])

    return Response(
        si.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=budget_stats.csv"}
    )