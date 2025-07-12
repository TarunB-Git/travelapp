from app import create_app
from app.extensions import db

app = create_app()

# auto‑create tables
with app.app_context():
    # print all registered routes for debugging
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} → {rule}")
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

