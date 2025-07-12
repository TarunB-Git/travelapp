from app.extensions import db
from datetime import datetime

transaction_recipient = db.Table(
    "transaction_recipient",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id"), primary_key=True),
    db.Column("person_id", db.Integer, db.ForeignKey("person.id"), primary_key=True),
)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    budget_category = db.Column(db.String(50), nullable=False)

    buyer_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    buyer = db.relationship("Person", backref="bought_transactions", foreign_keys=[buyer_id])

    recipients = db.relationship(
        "Person",
        secondary=transaction_recipient,
        backref=db.backref("received_transactions", lazy="dynamic")
    )

