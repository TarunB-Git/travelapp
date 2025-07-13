from app.models import Transaction, Person, Debt
from app.extensions import db

def recalculate_debts():
    db.session.query(Debt).delete()

    people = Person.query.all()
    txns = Transaction.query.all()

    for txn in txns:
        if not txn.recipients:
            continue
        per_head = txn.cost / len(txn.recipients)
        buyer = txn.buyer

        for rec in txn.recipients:
            if rec.id == buyer.id:
                continue  # buyer doesn't owe self

            # Skip if in same group
            if buyer.group_id and buyer.group_id == rec.group_id:
                continue

            debt = Debt.query.filter_by(debtor_id=rec.id, creditor_id=buyer.id, is_paid=False).first()
            if debt:
                debt.amount += per_head
            else:
                new_debt = Debt(debtor_id=rec.id, creditor_id=buyer.id, amount=per_head)
                db.session.add(new_debt)

    db.session.commit()