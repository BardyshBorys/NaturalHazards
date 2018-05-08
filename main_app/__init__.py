from flask import Flask
from flask_caching import Cache

app = Flask(__name__, static_url_path='/static')
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
