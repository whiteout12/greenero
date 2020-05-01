from app import db
from models import User


def check_user(username):
	if User.query.filter_by(username).first():
		return ['yes']
	else:
		return ['no']