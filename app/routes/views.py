from flask import Blueprint, render_template, redirect, url_for, request
from app.extensions import db
from app.models.person import Person
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.debt import Debt
from app.utils.debt_utils import recalculate_debts

views_bp = Blueprint("views_bp", __name__)

@views_bp.route("/")
def home():
    return redirect(url_for("views_bp.people_page"))

@views_bp.route("/people", methods=["GET", "POST"])
def people_page():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name and not Person.query.filter_by(name=name).first():
            p = Person(name=name)
            db.session.add(p)
            db.session.commit()
        return redirect(url_for(".people_page"))

    people = Person.query.all()
    return render_template("people.html", people=people)

@views_bp.route("/budgets", methods=["GET", "POST"])
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
                pid = int(request.form["person_id"])
                b = Budget.query.get(bid)
                p = Person.query.get(pid)
                if b and p:
                    b.person_id = p.id
                    db.session.commit()
            except (KeyError, ValueError):
                print("Invalid budget/person assign form")

        return redirect(url_for(".budgets_page"))

    budgets = Budget.query.all()
    people = Person.query.all()
    return render_template("budgets.html", budgets=budgets, people=people)

@views_bp.route("/transactions", methods=["GET", "POST"])
def transactions_page():
    if request.method == "POST":
        data = request.form
        try:
            rec_ids = [int(r) for r in data.getlist("recipient_ids")]
            buyer_id = int(data["buyer_id"])
            cost = float(data["cost"])
            item = data["item_name"].strip()
            cat = data["budget_category"].strip()
        except (KeyError, ValueError):
            print("Invalid form submission")
            return redirect(url_for(".transactions_page"))

        buyer = Person.query.get(buyer_id)
        recs = Person.query.filter(Person.id.in_(rec_ids)).all()
        if not buyer or len(recs) != len(rec_ids):
            print("Invalid buyer or recipient IDs")
            return redirect(url_for(".transactions_page"))

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
    return render_template(
        "transactions.html",
        people=people,
        budgets=budgets,
        transactions=txns
    )

@views_bp.route("/debts")
def debts_page():
    debts = Debt.query.all()
    return render_template("debts.html", debts=debts)

@views_bp.route("/history")
def history_page():
    txns = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template("history.html", transactions=txns)

