import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql://veveo:veveo123@10.28.218.164/lsh'
SQLALCHEMY_BINDS = {
                'db' : SQLALCHEMY_DATABASE_URI}
LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)s: %(message)s'
