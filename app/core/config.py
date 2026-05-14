import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "..", "instance", "travel_budget.db")
    SQLALCHEMY_BINDS = {
        "messages": "sqlite:///" + os.path.join(basedir, "..", "instance", "messages.db")
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
