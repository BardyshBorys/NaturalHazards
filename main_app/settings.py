NASA_EONET = {
    "categories": "https://eonet.sci.gsfc.nasa.gov/api/v2.1/categories",
    "events": "https://eonet.sci.gsfc.nasa.gov/api/v2.1/events",
    "sources": "https://eonet.sci.gsfc.nasa.gov/api/v2.1/sources",
    "layers": "https://eonet.sci.gsfc.nasa.gov/api/v2.1/layers",
}

EONET_CATEGORIES = [
    "Volcanoes", "Floods", "Snow", "Landslides", "Dust and Haze", "Temperature Extremes",
    "Earthquakes", "Wildfires", "Sea and Lake Ice", "Manmade", "Severe Storms", "Drought", "Water Color"
]

RSOE_EDIS_MAIN_URL = "https://hisz.rsoe.hu/ws/"
RSOE_EDIS_CATEGORIES = {
    "earthquakes": "eq",  # Earthquake data around the earth. The response data included the risk analisys.
    "geomagnetic_storm": "geostorm",  # Geomagnetis storm alert. Only "K" index alert.
    "us_npp": "us_npp",  # Nuclear Power Station Status Report. Only in the U.S.
    "tsunami_alert": "tsunami_alert",  # Tsunami alert messages based on PTWC.
    "volcano_report": "volcano_report",  # Volcano activity and eruption report around the Earth.
    "event_report": "event",  # Global disaster and emergency event database.
    "situation_update": "situation_update",  # Update of events. Coming soon
    "tropical_storm": "tropical_storms",  # Active tropical storms details.
    "extreme_weather": "noaaWeather",  # NOAA Extreme weather report. (US only)
    "solar_flare": "solar_flare",  # NOAA - Solar Flare Alert
    "airport_status": "airport_status"  # FAA - Airport status report in the US
}

EONET_DAY_LIMIT = 1000
RSOE_EDIS_DATA_LIMIT = 1000
