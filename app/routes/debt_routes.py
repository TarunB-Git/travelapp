from flask import Blueprint, render_template, request, redirect, url_for, session, Response
from app.models import Person, Debt
from app.extensions import db
from app.routes.views import login_required, admin_required
import csv
from io import StringIO

debt_bp = Blueprint("debt_bp", __name__)

@debt_bp.route("/debts", methods=["GET", "POST"])
@login_required
def debts_page():
    people = Person.query.all()
    debts = Debt.query.filter_by(is_paid=False).all()
    table = []

    for p in people:
        owed = [d for d in debts if d.debtor_id == p.id]
        by_person = {}

        for d in owed:
            # Skip intra-group debt
            if d.creditor.group_id and d.creditor.group_id == p.group_id:
                continue
            key = d.creditor.name
            by_person[key] = by_person.get(key, 0) + d.amount

        table.append({
            "person": p.name,
            "total": round(sum(by_person.values()), 2),
            "to": list(by_person.keys()),
            "per_person": by_person
        })

    return render_template("debts.html", table=table)

@debt_bp.route("/debts/mark-paid/<int:debt_id>")
@admin_required
def mark_debt_paid(debt_id):
    d = Debt.query.get_or_404(debt_id)
    d.is_paid = True
    db.session.commit()
    return redirect(url_for("debt_bp.debts_page"))

@debt_bp.route("/debts/delete/<int:debt_id>")
@admin_required
def delete_debt(debt_id):
    d = Debt.query.get_or_404(debt_id)
    db.session.delete(d)
    db.session.commit()
    return redirect(url_for("debt_bp.debts_page"))

@debt_bp.route("/export/debts.csv")
@admin_required
def export_debts():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Debtor", "Creditor", "Amount", "Status"])
    for d in Debt.query.all():
        writer.writerow([
            d.debtor.name,
            d.creditor.name,
            d.amount,
            "Paid" if d.is_paid else "Unpaid"
        ])
    return Response(si.getvalue(), mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=debts.csv"
    })