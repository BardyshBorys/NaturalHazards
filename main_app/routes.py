import json
import os

from flask import render_template
from markupsafe import Markup

from main_app import app
from utils import api_factory

access_id = os.environ.get('access_id')
secret_key = os.environ.get('secret_key')
rsoe_edis_api_key = os.environ.get('rsoe_edis_api_key')


@app.route('/')
@app.route('/index')
def index():
    factory = api_factory()
    return render_template(
        'index.html',
        title='WeatherAlerts',
        client_id=access_id,
        client_key=secret_key,
        eonet_categories=Markup(json.dumps(factory.eonet.categories)),
        rsoe_edis_categories=Markup(json.dumps(factory.rsoe_edis.categories))
    )
