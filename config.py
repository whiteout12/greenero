# default config
class BaseConfig(object):
	DEBUG = False
	SECRET_KEY = '\xad\xea\xbec\xe8\xbeK$)\xb6\x06\xc8\xda\x00\xb5!\xa2\xf0u.\xda \x98\xe2'
	SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/greenero_db'

# dev config
class DevelopmentConfig(BaseConfig):
	DEBUG = True
	#SECRET_KEY = 'mySecretKeyDev'


# prod config
class ProductionConfig(BaseConfig):
	DEBUG = False
	SECRET_KEY = 'mySecretKeyProd'