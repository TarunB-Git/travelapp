from app.core.extensions import db

class Group(db.Model):
    __tablename__ = "person_group"  # ← add this to avoid 'group' conflict

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    people = db.relationship("Person", back_populates="group")
