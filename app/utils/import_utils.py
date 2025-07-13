from openpyxl import load_workbook
from app.models import Person, Transaction
from app.extensions import db
from app.utils.debt_utils import recalculate_debts

def import_excel_transactions(file_stream):
    wb = load_workbook(file_stream)
    ws = wb.active

    for row in ws.iter_rows(min_row=2, values_only=True):
        item, cost, buyer_name, category, recipients_str = row
        buyer = Person.query.filter_by(name=buyer_name.strip()).first()
        if not buyer:
            continue
        recipient_names = [name.strip() for name in recipients_str.split(",")]
        recipients = Person.query.filter(Person.name.in_(recipient_names)).all()
        if not recipients:
            continue

        txn = Transaction(
            item_name=item,
            cost=float(cost),
            buyer_id=buyer.id,
            budget_category=category
        )
        txn.recipients.extend(recipients)
        db.session.add(txn)

    db.session.commit()
    recalculate_debts()
