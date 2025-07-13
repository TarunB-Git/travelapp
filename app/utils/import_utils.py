from openpyxl import load_workbook
from app.models import Person, Transaction
from app.extensions import db
from app.utils.debt_utils import recalculate_debts
from datetime import datetime

import pandas as pd
from openpyxl import load_workbook
from app.extensions import db
from app.models import Person, Transaction
from app.utils.debt_utils import recalculate_debts

def import_excel_transactions(file):
    ext = file.filename.lower().split(".")[-1]
    df = pd.read_excel(file) if ext == "xlsx" else pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower()

    for _, row in df.iterrows():
        buyer = Person.query.filter_by(name=str(row["buyer"]).strip()).first()
        if not buyer:
            continue

        rec_names = str(row["recipients"]).split(",")
        recipients = Person.query.filter(Person.name.in_([n.strip() for n in rec_names])).all()

        txn = Transaction(
            item_name=str(row["item"]).strip(),
            cost=float(row["cost"]),
            buyer_id=buyer.id,
            budget_category=str(row["category"]).strip(),
            timestamp=pd.to_datetime(row["timestamp"])
        )
        txn.recipients.extend(recipients)
        db.session.add(txn)

    db.session.commit()
    recalculate_debts()
