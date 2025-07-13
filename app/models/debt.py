from app.extensions import db

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

    debtor_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    creditor_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)

    debtor = db.relationship("Person", foreign_keys=[debtor_id], backref="debts_owed")
    creditor = db.relationship("Person", foreign_keys=[creditor_id], backref="debts_due")

    is_paid = db.Column(db.Boolean, default=False)