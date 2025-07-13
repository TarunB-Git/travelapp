from app.extensions import db

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    people = db.relationship("Person", back_populates="group")

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="people")
