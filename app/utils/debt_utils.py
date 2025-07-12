from app.extensions import db
from app.models.transaction import Transaction
from app.models.debt import Debt

def recalculate_debts() -> None:
    Debt.query.delete()
    db.session.flush()

    totals = {}
    for txn in Transaction.query.options(
        db.joinedload(Transaction.recipients)
    ).all():
        num = len(txn.recipients)
        if num == 0:
            continue
        share = txn.cost / num
        for rec in txn.recipients:
            if rec.id == txn.buyer_id:
                continue
            key = (txn.buyer_id, rec.id)
            totals[key] = totals.get(key, 0.0) + share

    for (lender_id, borrower_id), amount in totals.items():
        db.session.add(Debt(
            lender_id=lender_id,
            borrower_id=borrower_id,
            amount=amount
        ))
    db.session.commit()

