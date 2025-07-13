
from app import create_app
from app.extensions import db
from app.models.credentials import AdminCredentials

app = create_app()

with app.app_context():
    AdminCredentials.init()  # ← add this line

if __name__ == "__main__":
    app.run(debug=True)
