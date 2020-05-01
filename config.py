# default config
class BaseConfig(object):
	DEBUG = False
	SECRET_KEY = '\xad\xea\xbec\xe8\xbeK$)\xb6\x06\xc8\xda\x00\xb5!\xa2\xf0u.\xda \x98\xe2'
	#SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/greenero_db'
	SQLALCHEMY_DATABASE_URI = 'postgresql://bjorn:kerbus@192.168.1.6:5432/PROD01FAKK'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

# dev config
class DevelopmentConfig(BaseConfig):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'postgresql://bjorn:kerbus@whiteout.ddns.net:5432/PROD01FAKK'


# prod config
class ProductionConfig(BaseConfig):
	DEBUG = False
	#SECRET_KEY = 'mySecretKeyProd'
	SQLALCHEMY_DATABASE_URI = 'postgresql://bjorn:kerbus@localhost:5432/PROD01FAKK'