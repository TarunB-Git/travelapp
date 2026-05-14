
from app.core.app import create_app
from app.core.extensions import db, messages_db
from app.models.credentials import AdminCredentials

app = create_app()

with app.app_context():
    db.create_all()
    
    AdminCredentials.init()
    

if __name__ == "__main__":
    app.run(debug=True)
