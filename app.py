from flask import Flask
from config import Config
from models import db
from api import wuhan

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(wuhan)

