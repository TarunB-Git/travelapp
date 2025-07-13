import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///travel_budget.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    # ✅ this must be inside the class
    SQLALCHEMY_BINDS = {
        "messages": "sqlite:///instance/messages.db"
    }
