import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy, declarative_base


app = Flask(__name__, static_url_path='/templates')
app.config.from_object('config')

logging.basicConfig(format=app.config.get('LOG_FORMAT'))
logger = logging.getLogger(__name__)

db = SQLAlchemy(app)

from app import views, models
