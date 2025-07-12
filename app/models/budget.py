from app.extensions import db

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    daily_limit = db.Column(db.Float, nullable=True)
    total_limit = db.Column(db.Float, nullable=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=True)
    person = db.relationship("Person", backref="budgets")

