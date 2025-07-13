from flask import Blueprint, render_template, redirect, url_for, request, session
from app.extensions import db
from app.models.person import Person
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.debt import Debt
from app.utils.debt_utils import recalculate_debts
from functools import wraps
from collections import defaultdict

views_bp = Blueprint("views_bp", __name__)

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("access_granted"):
            return redirect(url_for("auth_bp.login"))
        return view_func(*args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("auth_bp.admin_login"))
        return view_func(*args, **kwargs)
    return wrapper

@views_bp.route("/")
def home():
    return redirect(url_for("views_bp.people_page"))

@views_bp.route("/people", methods=["GET", "POST"])
@login_required
def people_page():
    if request.method == "POST":
        if "delete_id" in request.form and session.get("admin"):
            p = Person.query.get(request.form["delete_id"])
            if p:
                db.session.delete(p)
                db.session.commit()
        elif "edit_id" in request.form and session.get("admin"):
            p = Person.query.get(request.form["edit_id"])
            new_name = request.form.get("new_name", "").strip()
            if p and new_name:
                p.name = new_name
                db.session.commit()
        else:
            name = request.form.get("name", "").strip()
            if name and not Person.query.filter_by(name=name).first():
                p = Person(name=name)
                db.session.add(p)
                db.session.commit()
        return redirect(url_for(".people_page"))

    people = Person.query.all()
    return render_template("people.html", people=people)

@views_bp.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets_page():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            cat = request.form.get("category", "").strip()
            if cat:
                b = Budget(
                    category=cat,
                    daily_limit=request.form.get("daily_limit") or None,
                    total_limit=request.form.get("total_limit") or None
                )
                db.session.add(b)
                db.session.commit()
        elif action == "assign":
            try:
                bid = int(request.form["budget_id"])
                pids = request.form.getlist("person_ids")
                b = Budget.query.get(bid)
                people = Person.query.filter(Person.id.in_(pids)).all()
                if b:
                    b.people = people
                    db.session.commit()
            except (KeyError, ValueError):
                pass
        elif action == "delete" and session.get("admin"):
            b = Budget.query.get(request.form.get("delete_id"))
            if b:
                db.session.delete(b)
                db.session.commit()
        return redirect(url_for(".budgets_page"))

    budgets = Budget.query.all()
    people = Person.query.all()
    return render_template("budgets.html", budgets=budgets, people=people)

@views_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions_page():
    if request.method == "POST":
        if "delete_id" in request.form and session.get("admin"):
            t = Transaction.query.get(request.form["delete_id"])
            if t:
                db.session.delete(t)
                db.session.commit()
                recalculate_debts()
        elif "edit_id" in request.form and session.get("admin"):
            t = Transaction.query.get(request.form["edit_id"])
            new_item = request.form.get("new_item_name", "").strip()
            if t and new_item:
                t.item_name = new_item
                db.session.commit()
        else:
            data = request.form
            try:
                rec_ids = [int(r) for r in data.getlist("recipient_ids")]
                buyer_id = int(data["buyer_id"])
                cost = float(data["cost"])
                item = data["item_name"].strip()
                cat = data["budget_category"].strip()
            except (KeyError, ValueError):
                return redirect(url_for(".transactions_page"))

            buyer = Person.query.get(buyer_id)
            recs = Person.query.filter(Person.id.in_(rec_ids)).all()
            if buyer and len(recs) == len(rec_ids):
                t = Transaction(
                    item_name=item,
                    cost=cost,
                    buyer_id=buyer.id,
                    budget_category=cat
                )
                t.recipients.extend(recs)
                db.session.add(t)
                db.session.commit()
                recalculate_debts()
        return redirect(url_for(".transactions_page"))

    people = Person.query.all()
    budgets = Budget.query.all()
    txns = Transaction.query.all()
    return render_template("transactions.html", people=people, budgets=budgets, transactions=txns)

@views_bp.route("/debts")
@login_required
def debts_page():
    debts = Debt.query.all()
    return render_template("debts.html", debts=debts)

from sqlalchemy import and_
from datetime import datetime

@views_bp.route("/history", methods=["GET", "POST"])
@login_required
def history_page():
    people = Person.query.all()
    budgets = Budget.query.all()
    txns = Transaction.query.order_by(Transaction.timestamp.desc())

    person_id = request.args.get("person_id")
    category = request.args.get("category")
    start = request.args.get("start_date")
    end = request.args.get("end_date")

    if person_id:
        txns = txns.filter(Transaction.buyer_id == person_id)
    if category:
        txns = txns.filter(Transaction.budget_category == category)
    if start:
        txns = txns.filter(Transaction.timestamp >= datetime.strptime(start, "%Y-%m-%d"))
    if end:
        txns = txns.filter(Transaction.timestamp <= datetime.strptime(end, "%Y-%m-%d"))

    return render_template("history.html", transactions=txns.all(), people=people, budgets=budgets)

@views_bp.route("/budget-stats")
@login_required
def budget_stats():
    from collections import defaultdict
    from datetime import date

    people = Person.query.all()
    budgets = Budget.query.all()
    transactions = Transaction.query.all()

    # Collect total spend per person per category for today
    spend_map = defaultdict(lambda: defaultdict(float))  # person_id → category → total

    today = date.today()
    for txn in transactions:
        if txn.timestamp.date() == today:
            split_cost = txn.cost / len(txn.recipients)
            for r in txn.recipients:
                spend_map[r.id][txn.budget_category] += split_cost

    # Build table: each row is a person, each column is spent/limit and remaining
    table_data = []
    donut_data = []

    for person in people:
        row = {"name": person.name, "categories": []}
        person_spend = spend_map.get(person.id, {})
        for b in budgets:
            if person not in b.people:
                continue
            spent = round(person_spend.get(b.category, 0), 2)
            limit = b.daily_limit or 0
            remaining = round(max(limit - spent, 0), 2)
            row["categories"].append({
                "category": b.category,
                "spent": spent,
                "limit": limit,
                "remaining": remaining
            })
            donut_data.append({
                "person": person.name,
                "category": b.category,
                "spent": spent,
                "remaining": remaining
            })
        table_data.append(row)

    return render_template("budget_stats.html", table=table_data, donut_data=donut_data)

    