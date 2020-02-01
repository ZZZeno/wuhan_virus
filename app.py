from flask import Flask
from models import db
from api import wuhan

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

db.init_app(app)

app.register_blueprint(wuhan)

