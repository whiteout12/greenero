# default config
class BaseConfig(object):
	DEBUG = False
	SECRET_KEY = '\xad\xea\xbec\xe8\xbeK$)\xb6\x06\xc8\xda\x00\xb5!\xa2\xf0u.\xda \x98\xe2'
<<<<<<< HEAD
	#SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/greenero_db'
	SQLALCHEMY_DATABASE_URI = 'postgresql://bjorn:kerbus@192.168.1.6:5432/PROD01FAKK'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
=======
	SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/greenero_db'
>>>>>>> 400a8281184cc1ca8bb014707cc75b71f73bdf25

# dev config
class DevelopmentConfig(BaseConfig):
	DEBUG = True
	#SECRET_KEY = 'mySecretKeyDev'


# prod config
class ProductionConfig(BaseConfig):
	DEBUG = False
	SECRET_KEY = 'mySecretKeyProd'