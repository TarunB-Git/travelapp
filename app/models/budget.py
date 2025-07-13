from app.extensions import db

budget_person = db.Table(
    "budget_person",
    db.Column("budget_id", db.Integer, db.ForeignKey("budget.id")),
    db.Column("person_id", db.Integer, db.ForeignKey("person.id"))
)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    daily_limit = db.Column(db.Float, nullable=True)
    total_limit = db.Column(db.Float, nullable=True)

    people = db.relationship("Person", secondary=budget_person, backref="budgets")