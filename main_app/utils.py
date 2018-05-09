import os
import requests
from geojson import Feature, FeatureCollection
from main_app import cache
from settings import NASA_EONET, EONET_DAY_LIMIT, EONET_CATEGORIES
from settings import RSOE_EDIS_MAIN_URL, RSOE_EDIS_CATEGORIES, RSOE_EDIS_DATA_LIMIT


class Factory(object):
    @property
    def eonet(self):
        return EONET()

    @property
    def rsoe_edis(self):
        return RSOE_EDIS()


class EONET(object):

    @property
    @cache.cached(timeout=1360, key_prefix='eonet_api_call')
    def categories(self):
        return {
            name: self._get_data_by_category(_id)
            for name, _id in self.categories_ids if name in EONET_CATEGORIES
        }

    @property
    def categories_ids(self):
        """
        Purpose: get all categories and their ids
        :return:
        """
        return [
            (item['title'], item['id']) for item in requests.get(NASA_EONET['categories']).json()["categories"]
        ]

    @staticmethod
    def _event_to_json_feature(event):
        """
        Purpose to create geojson output from eonet data
        :param event: dict, with eonet data
        :return: geojson feature class instance
        """
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

    def _geojson_from_data(self, data):
        """
        Purpose to form data into geojson format by help of geojson lib
        :param data: raw data from api call
        :return: geojson class object, Feature collection class object with populated data in it
        """
        events = data.get('events')
        if events and len(events) > 1:
            feature_collection = [self._event_to_json_feature(event) for event in events]
            return FeatureCollection(feature_collection)
        elif events and len(events) == 1:
            return FeatureCollection([self._event_to_json_feature(events[0])])
        else:
            return FeatureCollection([])

    def _get_data_by_category(self, _id):
        """
        Purpose get events by category by id with default days limit which set in settings.py
        :param _id: int, category id
        :return: geojson class object
        """
        data_query = 'days=%s' % EONET_DAY_LIMIT
        url = '%s/%s?%s' % (NASA_EONET['categories'], _id, data_query)
        return self._geojson_from_data(requests.get(url).json())

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class RSOE_EDIS(object):

    @property
    @cache.cached(timeout=1360, key_prefix='rsoe_edis_api_call')
    def categories(self):
        rsoe_edis_categories = sorted(RSOE_EDIS_CATEGORIES.keys())
        return {
            category: self.get_category(RSOE_EDIS_CATEGORIES.get(category))
            for category in rsoe_edis_categories
        }

    def get_category(self, category):
        url = "{main_url}/{category_name}/?api_key={api_key}&limit={event_limit}".format(
            main_url=RSOE_EDIS_MAIN_URL,
            category_name=category,
            api_key=os.environ.get('rsoe_edis_api_key'),
            event_limit=RSOE_EDIS_DATA_LIMIT,
        )
        response = requests.post(url)
        return self._geojson_from_data(response.json())

    def _geojson_from_data(self, data):
        """
        Purpose to form data into geojson format by help of geojson lib
        :param data: raw data from api call
        :return: geojson class object, Feature collection class object with populated data in it
        """
        events = isinstance(data, list) and data or data.get('result')
        if events and len(events) > 1:
            feature_collection = [
                self._event_to_json_feature(event) for event in events
                if event.get('longitude')
            ]
            return FeatureCollection(feature_collection)
        elif events and len(events) == 1:
            return FeatureCollection([self._event_to_json_feature(events[0])])
        else:
            return FeatureCollection([])

    @staticmethod
    def _event_to_json_feature(event):
        """
        Purpose to create geojson output from eonet data
        :param event: dict, with eonet data
        :return: geojson feature class instance
        """
        longitude = event.get('longitude', 0)
        latitude = event.get('latitude', 0)
        if isinstance(longitude, (unicode, str)):
            longitude = float(longitude)
        if isinstance(latitude, (unicode, str)):
            latitude = float(latitude)
        geometry = {
            'type': 'Point',
            'coordinates': [longitude, latitude]
        }
        del event['longitude']
        del event['latitude']
        feature = Feature(
            properties=event,
            geometry=geometry
        )
        return feature


def api_factory():
    return Factory()
