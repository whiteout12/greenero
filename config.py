# default config
class BaseConfig(object):
	DEBUG = False
	SECRET_KEY = 'mySecretKeyBase'

# dev config
class DevelopmentConfig(BaseConfig):
	DEBUG = True
	SECRET_KEY = 'mySecretKeyDev'


# prod config
class ProductionConfig(BaseConfig):
	DEBUG = False
	SECRET_KEY = 'mySecretKeyProd'