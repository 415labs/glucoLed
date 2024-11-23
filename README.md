# GlucoLed
Glucose monitoring system with RGB LED indicators.

## Description

This module interfaces with LibreLink Up to fetch glucose data and displays different colors on an RGB LED based on glucose levels.

## Getting Started

### Hardware setup on the Raspberry Pi (3):
* Connect: RGB led common anode connected to the Rapberry Pi +3.3v
* RGB Led red terminal connected to gpio1
* RGB Led Green terminal connected to gpio2
* RGB Led Blue terminal connected to gpio3

### Dependencies
* create a virtual environment: python3 -m venv glucoLed

Within the virtual environment: 
* pip install libre-linkup-py
* pip install Pydantic
* pip install pytz
* pip install RPi.GPIO

### Installing

* Create a ./glucoLed/.env file with:
```
LIBRE_LINK_UP_USERNAME=<Libre Linkup username>
LIBRE_LINK_UP_PASSWORD=<Libre Linkup password>
LIBRE_LINK_UP_URL=https://api.libreview.io
LIBRE_LINK_UP_VERSION=4.7.0  # Optional
```

### Executing program

```
./glucoLed/bin/python ./glucoLed/glucoLed.py
```

### Tip (hack)

* You may have to do the following:
* In glucoLed/lib/python3.11/site-packages/pytz/__init__.py
* Replace: zone = _case_insensitive_zone_lookup(_unmunge_zone(zone))
* With: zone = "US/Pacific"
