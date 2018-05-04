import folium

from settings import aerisweather
# from utils import get_all_nasa_eonet_layers



base_map = folium.Map(location=[40.7, -73.9])


folium.TileLayer(
    tiles='https://maps{{s}}.aerisapi.com/{client_id}_{client_key}/alerts/{{z}}/{{x}}/{{y}}/-5minutes.png'.format(
        client_id=aerisweather['access_id'],
        client_key=aerisweather['secret_key']
    ),
    attr='&copy;AerisWeather',
    name='aerisapi_alerts',
    subdomains='1234',
    overlay=True
).add_to(base_map)

# for layer in get_all_nasa_eonet_layers():
#     layer.add_to(base_map)

folium.LayerControl().add_to(base_map)

base_map.save("result_map.html")
