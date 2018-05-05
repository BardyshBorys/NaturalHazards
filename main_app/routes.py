import json
import os

import requests
from flask import jsonify
from flask import render_template
from flask import request
from markupsafe import Markup
from geojson import Feature, FeatureCollection
from main_app import app
from settings import CATEGORIES_COLORS
from settings import NASA_EONET

access_id = os.environ.get('access_id')
secret_key = os.environ.get('secret_key')


def _event_to_json_feature(event):
    feature = Feature(
        properties={
            "name": event.get('title', ''),
            "id": event.get('id', ''),
            "description": event.get('description', ''),
            "category": event.get('categories') and event.get('categories')[0].get('title') or '',
            "source": event.get('sources', '')
        },
        geometry=event.get('geometries')[0]
    )
    return feature


def _form_geojson(data):
    events = data.get('events')
    if events and len(events) > 1:
        feature_collection = {
            "type": "FeatureCollection",
            "features": [
                _event_to_json_feature(event) for event in events
            ]}
        return jsonify(FeatureCollection(feature_collection))
    elif events and len(events) == 1:
        return jsonify(Feature(_event_to_json_feature(events[0])))
    else:
        return jsonify({})


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
def get_data_by_category():
    """
    Purpose: query the eonet categories api by default get all data by all categories
    :param kwargs:
    :return:
    """
    data_query = '&'.join(['%s=%s' % (key, val) for key, val in request.form.iteritems() if key != 'category_id'])
    url = '%s/%s?%s' % (NASA_EONET['categories'], request.form.get('category_id'), data_query)
    return _form_geojson(requests.get(url).json())
