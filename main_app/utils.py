import requests

from settings import NASA_EONET


def get_raw_eonet_data_reference():
    return {
        key: requests.get(item).json() for key, item in NASA_EONET.iteritems()
    }


def get_all_categories():
    return {
        item['title']: item
        for item in requests.get(NASA_EONET['categories']).json()["categories"]
    }


def get_categories_id():
    return {
        item['title']: item['id']
        for item in requests.get(NASA_EONET['categories']).json()["categories"]
    }


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
        return requests.get(url).json()
    else:
        return requests.get(NASA_EONET['events']).json()


def get_data_by_category(**kwargs):
    """
    Purpose: query the eonet categories api by default get all data by all categories
    :param kwargs:
    :return:
    """
    if kwargs.get('category_id'):
        data_query = '&'.join(['%s=%s' % (key, val) for key, val in kwargs.iteritems() if key != 'category_id'])
        url = '%s/%s?%s' % (NASA_EONET['categories'], kwargs.get('category_id'), data_query)
        return requests.get(url).json()
    else:
        categories = get_all_categories()
        return {
            key: requests.get(value['link']).json() for key, value in categories.iteritems()
        }
