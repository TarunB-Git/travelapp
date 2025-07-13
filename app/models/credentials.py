import bcrypt
from app.extensions import db

class AdminCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_password_hash = db.Column(db.String(128))
    admin_password_hash = db.Column(db.String(128))

    @staticmethod
    def get():
        return AdminCredentials.query.first()

    @staticmethod
    def init():
        if not AdminCredentials.get():
            db.session.add(AdminCredentials(
                access_password_hash=bcrypt.hashpw(b"default", bcrypt.gensalt()).decode(),
                admin_password_hash=bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode()
            ))
            db.session.commit()

    def check_access_password(self, raw: str) -> bool:
        return bcrypt.checkpw(raw.encode(), self.access_password_hash.encode())

    def check_admin_password(self, raw: str) -> bool:
        return bcrypt.checkpw(raw.encode(), self.admin_password_hash.encode())

    def set_access_password(self, raw: str) -> None:
        self.access_password_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def set_admin_password(self, raw: str) -> None:
        self.admin_password_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
