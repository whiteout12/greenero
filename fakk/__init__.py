from flask import Flask #make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
import psycopg2
from flask_mail import Mail, Message
import psycopg2
import os

# config

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
mail = Mail(app)

from fakk.site.main.routes import main
from fakk.site.user.routes import user

from fakk.site.relations.routes import contacts
from fakk.site.invoices.routes import invoices

from fakk.api.relations.routes import relations_api
from fakk.api.invoices.routes import invoices_api


app.register_blueprint(main)
app.register_blueprint(user)

app.register_blueprint(contacts)
app.register_blueprint(invoices)

app.register_blueprint(relations_api)
app.register_blueprint(invoices_api)

# get user by id, used by login_manager
login_manager.login_view = "user.login"
login_manager.login_message = ""

@login_manager.user_loader
def load_user(user_id):
	from fakk.models import User
	return User.query.filter(User.userid == int(user_id)).first()