import logging

from flask import Flask
from flask_caching import Cache

from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
db = SQLAlchemy()
ma = Marshmallow()
cache = Cache()


LOGGER = logging.getLogger('url_shortner')

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.DEBUG)

def create_app(config_class=Config, **kwargs):
    app.config.from_object(Config)
    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://redis:6379/2'})
    # cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    migrate = Migrate(app, db)

    return app
