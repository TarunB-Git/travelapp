from app.extensions import db

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    lender = db.relationship("Person", foreign_keys=[lender_id], backref="lent_debts")
    borrower = db.relationship("Person", foreign_keys=[borrower_id], backref="owed_debts")

    __table_args__ = (
        db.UniqueConstraint("lender_id", "borrower_id", name="_lender_borrower_uc"),
    )

