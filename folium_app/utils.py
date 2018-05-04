import json
import os
from datetime import datetime

import folium
import requests
from jinja2 import Environment, PackageLoader, Template
from six import binary_type, text_type

from settings import nasa_eonet_layers, nasa_eonet_layers_include

ENV = Environment(loader=PackageLoader('folium', 'templates'))


class CustomTileLayer(folium.TileLayer):
    def __init__(self, tiles='OpenStreetMap', min_zoom=1, max_zoom=18,
                 attr=None, API_key=None, detect_retina=False,
                 name=None, overlay=False, _options=None,
                 control=True, no_wrap=False, subdomains='abc'):
        self.tile_name = (name if name is not None else
                          ''.join(tiles.lower().strip().split()))
        super(CustomTileLayer, self).__init__(name=self.tile_name, overlay=overlay,
                                        control=control)
        self._name = 'TileLayer'
        self._env = ENV

        options = {
            'minZoom': min_zoom,
            'maxZoom': max_zoom,
            'noWrap': no_wrap,
            'attribution': attr,
            'subdomains': subdomains,
            'detectRetina': detect_retina,
        }
        if _options:
            options.update(_options)
        self.options = json.dumps(options, sort_keys=True, indent=2)

        self.tiles = ''.join(tiles.lower().strip().split())
        if self.tiles in ('cloudmade', 'mapbox') and not API_key:
            raise ValueError('You must pass an API key if using Cloudmade'
                             ' or non-default Mapbox tiles.')
        templates = list(self._env.list_templates(
            filter_func=lambda x: x.startswith('tiles/')))
        tile_template = 'tiles/'+self.tiles+'/tiles.txt'
        attr_template = 'tiles/'+self.tiles+'/attr.txt'

        if tile_template in templates and attr_template in templates:
            self.tiles = self._env.get_template(tile_template).render(API_key=API_key)  # noqa
            self.attr = self._env.get_template(attr_template).render()
        else:
            self.tiles = tiles
            if not attr:
                raise ValueError('Custom tiles must'
                                 ' also be passed an attribution.')
            if isinstance(attr, binary_type):
                attr = text_type(attr, 'utf8')
            self.attr = attr

        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            var {{this.get_name()}} = L.tileLayer(
                '{{this.tiles}}',
                {{ this.options }}
                ).addTo({{this._parent.get_name()}});
        {% endmacro %}
        """)  # noqa


def filter_layers(layers):
    return [
        layer for layer in layers
        if layer['name'] in nasa_eonet_layers_include
    ]


def get_all_nasa_eonet_layers(_date=None):
    if not _date:
        _date = '{DATE:%Y-%m-%d}'.format(DATE=datetime.utcnow())
    response = requests.get(nasa_eonet_layers)
    if response.status_code == 200 and response.json().get('categories'):
        layers = filter_layers(response.json().get('categories')[0].get('layers'))
        for layer in layers:
            parameters = layer['parameters'][0]
            image_format = parameters.get('FORMAT', 'image/jpeg').split('/')[-1]
            url = '{main_url}/{layer_url}'.format(
                main_url=layer['serviceUrl'].rpartition('/')[0],
                layer_url=os.path.join(
                    layer['name'], 'default', _date, parameters.get('TILEMATRIXSET', ''), '{z}/{x}', '{y}.%s' % image_format
                )
            )
            if layer['serviceUrl'].endswith('wms.php'):
                yield folium.features.WmsTileLayer(
                    name=layer['name'],
                    url=layer['serviceUrl'],
                    layers=layer['name'],
                    transparent=True,
                    fmt=parameters.get('FORMAT', 'image/jpeg'),
                    attr='&copy;Nasa;EONET',
                    TIME="%sT00:00:00Z" % _date
                )
                # "https://gibs-c.earthdata.nasa.gov/wms/wms.php?TIME=2015-06-25T00:00:00Z&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&LAYERS=MODIS_Fires_Terra&WIDTH=256&HEIGHT=256&SRS=EPSG%3A4326&STYLES=&BBOX=-81%2C27%2C-76.5%2C31.5"
                # "https://map2.vis.earthdata.nasa.gov/wms/wms.php?service=WMS&request=GetMap&layers=MODIS_Fires_All&styles=&format=image%2Fpng&transparent=true&version=1.1.1&height=256&width=256&srs=EPSG%3A3857&bbox=-8140237.764258132,5009377.085697314,-7827151.69640205,5322463.153553395"
            elif layer['serviceUrl'].endswith('.cgi'):
                tile_layer = CustomTileLayer(
                    url,
                    _options={'crs': 'EPSG4326'},
                    attr='&copy;NASA;EONET',
                    name=layer['name'],
                    overlay=True
                )
                yield tile_layer

