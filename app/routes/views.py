from flask import Blueprint, render_template, redirect, url_for, request, session
from app.extensions import db
from app.models.person import Person
from app.models.group import Group
from flask import jsonify

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
    return redirect(url_for("views_bp.transactions_page"))


@views_bp.route("/people", methods=["GET", "POST"])
def people_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        group_id = request.form.get("group_id")
        if name and not Person.query.filter_by(name=name).first():
            person = Person(name=name, group_id=group_id if group_id else None)
            db.session.add(person)
            db.session.commit()
        return redirect(url_for(".people_page"))

    people = Person.query.all()
    groups = Group.query.all()
    return render_template("people.html", people=people, groups=groups)

@views_bp.route("/groups", methods=["POST"])
def create_group():
    name = request.form.get("group_name", "").strip()
    if name and not Group.query.filter_by(name=name).first():
        group = Group(name=name)
        db.session.add(group)
        db.session.commit()
    return redirect(url_for(".people_page"))

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
    from app.extensions import db

    if request.method == "POST":
        try:
            data = request.form
            buyer_id = int(data["buyer_id"])
            cost = float(data["cost"])
            item = data["item_name"].strip()
            category = data["budget_category"].strip()
            rec_ids = list(map(int, data.getlist("recipient_ids")))

            buyer = Person.query.get(buyer_id)
            recs = Person.query.filter(Person.id.in_(rec_ids)).all()

            if not buyer or not recs:
                return "Invalid buyer or recipients", 400

            t = Transaction(
                item_name=item,
                cost=cost,
                buyer_id=buyer.id,
                budget_category=category
            )
            t.recipients.extend(recs)
            db.session.add(t)
            db.session.commit()

            from app.utils.debt_utils import recalculate_debts
            recalculate_debts()

            return redirect(url_for("views_bp.transactions_page"))

        except Exception as e:
            db.session.rollback()
            return f"Error: {e}", 500

    people = Person.query.all()
    budgets = Budget.query.all()
    txns = Transaction.query.order_by(Transaction.timestamp.desc()).all()

    return render_template("transactions.html", people=people, budgets=budgets, transactions=txns)

import pandas as pd
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename

@views_bp.route("/transactions/import", methods=["POST"])

def import_transactions():
    file = request.files.get("file")
    if not file:
        flash("No file uploaded.", "danger")
        return redirect(url_for("views_bp.transactions_page"))

    filename = file.filename.lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(file)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        flash("Unsupported file format. Please upload a .csv or .xlsx file.", "danger")
        return redirect(url_for("views_bp.transactions_page"))

    required_cols = {"timestamp", "item", "cost", "buyer", "category", "recipients"}
    if not required_cols.issubset(set(df.columns.str.lower())):
        flash("Missing required columns in file.", "danger")
        return redirect(url_for("views_bp.transactions_page"))

    for _, row in df.iterrows():
        try:
            buyer = Person.query.filter_by(name=str(row["buyer"]).strip()).first()
            if not buyer:
                continue

            rec_names = str(row["recipients"]).split(",")
            recipients = Person.query.filter(Person.name.in_([n.strip() for n in rec_names])).all()

            txn = Transaction(
                item_name=str(row["item"]),
                cost=float(row["cost"]),
                buyer_id=buyer.id,
                budget_category=str(row["category"]),
                timestamp=pd.to_datetime(row["timestamp"])
            )
            txn.recipients.extend(recipients)
            db.session.add(txn)
        except Exception as e:
            flash(f"Error on row: {e}", "warning")

    db.session.commit()
    recalculate_debts()
    flash("Transactions imported successfully!", "success")
    return redirect(url_for("views_bp.transactions_page"))


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
    from datetime import date, datetime

    people = Person.query.all()
    groups = sorted(set(p.group.name for p in people if p.group))
    budgets = Budget.query.all()

    selected_person = request.args.get("person")
    selected_group = request.args.get("group")
    selected_date = request.args.get("date")
    try:
        filter_date = datetime.strptime(selected_date, "%Y-%m-%d").date() if selected_date else date.today()
    except:
        filter_date = date.today()

    txns = Transaction.query.all()

    # person_id → category → total
    spend_map = defaultdict(lambda: defaultdict(float))

    for txn in txns:
        if txn.timestamp.date() != filter_date or not txn.recipients:
            continue
        share = txn.cost / len(txn.recipients)
        for rec in txn.recipients:
            spend_map[rec.id][txn.budget_category] += share

    table_data = []
    donut_data = []

    for person in people:
        if selected_person and person.name != selected_person:
            continue
        if selected_group and (not person.group or person.group.name != selected_group):
            continue

        person_spend = spend_map.get(person.id, {})
        row = {"name": person.name, "categories": []}

        # Show all budgets, even if not spent
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
                "remaining": remaining,
                "overrun": spent > limit
            })
            donut_data.append({
                "person": person.name,
                "category": b.category,
                "spent": spent,
                "remaining": remaining
            })

        if row["categories"]:
            table_data.append(row)

    return render_template(
        "budget_stats.html",
        table=table_data,
        donut_data=donut_data,
        people=people,
        groups=groups,
        selected_person=selected_person,
        selected_group=selected_group,
        selected_date=filter_date.isoformat()
    )
    
@views_bp.route("/groups", methods=["GET", "POST"])
@admin_required
def group_page():
    from app.extensions import db
    people = Person.query.all()
    groups = Group.query.order_by(Group.name).all()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            name = request.form.get("name", "").strip()
            if name and not Group.query.filter_by(name=name).first():
                db.session.add(Group(name=name))
                db.session.commit()

        elif action == "assign":
            person_id = request.form.get("person_id")
            group_id = request.form.get("group_id")
            person = Person.query.get(person_id)
            group = Group.query.get(group_id)
            if person and group:
                person.group_id = group.id
                db.session.commit()

        return redirect(url_for("views_bp.group_page"))

    return render_template("groups.html", people=people, groups=groups)
    
@views_bp.route("/toggle-theme", methods=["POST"])
def toggle_theme():
    theme = session.get("theme", "light")
    session["theme"] = "dark" if theme == "light" else "light"
    return "", 204

@views_bp.route("/get-theme")
def get_theme():
    return jsonify({"theme": session.get("theme", "light")})
