from flask import Flask
from .models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blah.sqlite"
app.config["SECRET_KEY"] = "nopethisissekret"
db.init_app(app)

with app.app_context():
    db.create_all()

from . import views
