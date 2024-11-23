Hardware setup on the Raspberry Pi (3):

Connect: RGB led common anode connected to the Rapberry Pi +3.3v

RGB Led red terminal connected to gpio1

RGB Led Green terminal connected to gpio2

RGB Led Blue terminal connected to gpio3

python3 -m venv glucoLed

./glucoLed/bin/pip install libre-linkup-py

./glucoLed/bin/pip install Pydantic

./glucoLed/pip install pytz

./glucoLed/pip install RPi.GPIO


Create ./glucoLed/.env

LIBRE_LINK_UP_USERNAME=<Libre Linkup username>

LIBRE_LINK_UP_PASSWORD=<Libre Linkup password>

LIBRE_LINK_UP_URL=https://api.libreview.io

LIBRE_LINK_UP_VERSION=4.7.0  # Optional


In glucoLed/lib/python3.11/site-packages/pytz/__init__.py

Replace: zone = _case_insensitive_zone_lookup(_unmunge_zone(zone))

With: zone = "US/Pacific"

(line 181)


Run app:

./glucoLed/bin/python ./glucoLed/glucoLed.py
