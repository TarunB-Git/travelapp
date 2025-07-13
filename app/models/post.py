from app.extensions import messages_db as db
from datetime import datetime

class MessagePost(db.Model):
    __bind_key__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    author = db.Column(db.String(50), default="Anonymous")
    image_path = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
