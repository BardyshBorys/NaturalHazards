import os
import requests
import json
from flask import render_template
from flask import jsonify
from main_app import app
from utils import get_all_categories
from settings import NASA_EONET
from settings import CATEGORIES_COLORS
from markupsafe import Markup


access_id = os.environ.get('access_id')
secret_key = os.environ.get('secret_key')


def _get_categories_id():
    """
    Purpose: get all categories and their ids
    :return:
    """
    return {
        item['title']: item['id']
        for item in requests.get(NASA_EONET['categories']).json()["categories"]
    }


@app.route('/')
@app.route('/index')
def index():
    return render_template(
        'index.html',
        title='WeatherAlerts',
        client_id=access_id,
        client_key=secret_key,
        categories=Markup(json.dumps(_get_categories_id())),
        categories_colors=Markup(json.dumps(CATEGORIES_COLORS))
    )


@app.route('/get_raw_eonet_data_reference', methods=['POST'])
def get_raw_eonet_data_reference():
    return jsonify({
        key: requests.get(item).json() for key, item in NASA_EONET.iteritems()
    })


@app.route('/get_categories_id', methods=['POST'])
def get_categories_id():
    """
    Purpose: get all categories and their ids
    :return:
    """
    return jsonify({
        item['title']: item['id']
        for item in requests.get(NASA_EONET['categories']).json()["categories"]
    })


@app.route('/get_data_by_event', methods=['POST'])
def get_data_by_event(**kwargs):
    """
    Purpose: query the eonet events api
    :param kwargs: should only include the default parameters like: limit, days, source, status
           Example: limit = 5, days = 20, source = 'InciWeb', status = 'open'
    :return: dict, events data
    """
    data_query = '&'.join(['%s=%s' % (key, val) for key, val in kwargs.iteritems()])
    if data_query:
        url = '%s?%s' % (NASA_EONET['events'], data_query)
        return jsonify(requests.get(url).json())
    else:
        return jsonify(requests.get(NASA_EONET['events']).json())


@app.route('/get_data_by_category', methods=['POST'])
def get_data_by_category(**kwargs):
    """
    Purpose: query the eonet categories api by default get all data by all categories
    :param kwargs:
    :return:
    """
    if kwargs.get('category_id'):
        data_query = '&'.join(['%s=%s' % (key, val) for key, val in kwargs.iteritems() if key != 'category_id'])
        url = '%s/%s?%s' % (NASA_EONET['categories'], kwargs.get('category_id'), data_query)
        return jsonify(requests.get(url).json())
    else:
        categories = get_all_categories()
        return jsonify({
            key: requests.get(value['link']).json() for key, value in categories.iteritems()
        })
