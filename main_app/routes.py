import json
import os

import requests
from flask import render_template
from geojson import Feature, FeatureCollection
from markupsafe import Markup

from main_app import app
from settings import NASA_EONET, CATEGORIES, DAY_LIMIT

access_id = os.environ.get('access_id')
secret_key = os.environ.get('secret_key')


def _event_to_json_feature(event):
    geometry = event.get('geometries')[0]
    geometry['coordinates'] = geometry['coordinates']
    event_date = event.get('geometries')[0].get('date')
    if 'date' in geometry.keys():
        del geometry['date']
    feature = Feature(
        properties={
            "name": event.get('title', ''),
            "id": event.get('id', ''),
            "description": event.get('description', ''),
            "category": event.get('categories') and event.get('categories')[0].get('title') or '',
            "source": event.get('sources', ''),
            "date": event_date
        },
        geometry=geometry
    )
    return feature


def _form_geojson(data):
    events = data.get('events')
    if events and len(events) > 1:
        feature_collection = [_event_to_json_feature(event) for event in events]
        return FeatureCollection(feature_collection)
    elif events and len(events) == 1:
        return FeatureCollection([_event_to_json_feature(events[0])])
    else:
        return FeatureCollection([])


def _get_categories_ids():
    """
    Purpose: get all categories and their ids
    :return:
    """
    return [
        (item['title'], item['id']) for item in requests.get(NASA_EONET['categories']).json()["categories"]
    ]


def _get_data_by_category(_id):
    """

    :param id:
    :return:
    """
    data_query = 'days=%s' % DAY_LIMIT
    url = '%s/%s?%s' % (NASA_EONET['categories'], _id, data_query)
    return _form_geojson(requests.get(url).json())


@app.route('/')
@app.route('/index')
def index():
    categories = {name: _get_data_by_category(_id) for name, _id in _get_categories_ids() if name in CATEGORIES}
    return render_template(
        'index.html',
        title='WeatherAlerts',
        client_id=access_id,
        client_key=secret_key,
        all_categories=Markup(json.dumps(categories))
    )
