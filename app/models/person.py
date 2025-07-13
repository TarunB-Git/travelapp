from app.extensions import db

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))


