# NaturalHazards
Purpose of this project catch the latest Natural Hazards alarms and show on the map

### Starting progect localy
    1. pip install requirements.txt
    2. python wsgi.py
    2.1. get populated data from RSOE EDIS data shoud be exported environment api key "rsoe_edis_api_key"
    Example :
        export rsoe_edis_api_key=<api key>

### File description
    main_app/routes.py - contains actual view for the map
    main_app/setting.py - contains global setting for the web app
    main_app/utils.py - contains bridge for comunicating with different NATURAL HAZARD API
    main_app/templates/index.html - contains main js code
    main_app/static/css/custom.css - contains custom css
    main_app/static/js/custom_markers.js - contains custom js code mainly markers for leaflet
    main_app/static/img/natural_hazard_icons - folder contains all images for markers
    main_server.py- development web server executable
    wsgi.py - development web server executable used as reference on openshift service

alpha version of the site located here: http://natural-hazards-natural-hazards.193b.starter-ca-central-1.openshiftapps.com/