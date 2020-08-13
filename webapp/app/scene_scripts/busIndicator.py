from scene_scripts.Bus import Bus
from scene_scripts.BusMinQueue import BusMinQueue

import os
import time
import dotenv
import urllib.request
import urllib.response
from datetime import datetime
from google.transit import gtfs_realtime_pb2
from phue import Bridge

dotenv.load_dotenv(dotenv.find_dotenv())
# constants
lat_me = float(os.getenv('MYLAT'))
lon_me = float(os.getenv('MYLON'))
API_KEY = os.getenv('API_KEY')
bridge_ip = os.getenv('BRIDGE_IP')

# connect to the bridge
bridge = Bridge(bridge_ip)
bridge.connect()
# create a light grouping and turn them on
lr_lamp = [1, 4]
command = {'on': True, 'bri': 127}
bridge.set_light(lr_lamp, command)

"""
EFFECTS: pulls realtime transit data from TransLink and estimates the distance from
the users location. Changes the colors on Philips Hue lights using traffic light logic
when buses are approaching. 
"""


def run_buswatch(route_id: str, direction: str, runtime_sec: int, freq_sec: int) -> None:
    if (runtime_sec / freq_sec) > 1000:
        print("Flashy lights bb")
        return
    # blink the lights to indicate we would exceed the 1000 requests per day limit
    keep_running = runtime_sec // freq_sec  # // is int division in Python
    if direction.lower() == 'westbound' or 'northbound':
        d = 1
    else:
        d = 0

    bus_pq = BusMinQueue()
    while keep_running:
        feed = gtfs_realtime_pb2.FeedMessage()
        # print('https://gtfs.translink.ca/v2/gtfsposition?apikey=' + API_KEY)
        response = urllib.request.urlopen('https://gtfs.translink.ca/v2/gtfsposition?apikey=' + API_KEY)
        feed.ParseFromString(response.read())

        for entity in feed.entity:
            if (entity.HasField('vehicle') and
                    entity.vehicle.trip.route_id == route_id and
                    entity.vehicle.trip.direction_id == d):
                lat = entity.vehicle.position.latitude
                lon = entity.vehicle.position.longitude
                vehicle_id = entity.vehicle.vehicle.id
                bus_time = datetime.fromtimestamp(int(entity.vehicle.timestamp))

                bus = Bus(vehicle_id, route_id)
                b = bus_pq.find(bus)  # set b to the bus
                # TODO: if a bus hasn't been updated in over 5 minutes drop it from the list / don't add it. Something
                #       to account for when buses stop running but the bus stays in the bus list. Maybe if a bus that is
                #       in the list is no longer appearing in the GTFS data then drop it
                if b is None and bus_not_passed(lat, lon, direction):
                    bus.add_gps_point(lat, lon, bus_time)
                    bus_pq.push((bus.predicted_distance(lat_me, lon_me), bus))
                elif bus_not_passed(lat, lon, direction):
                    b[1].add_gps_point(lat, lon, bus_time)
                    bus_pq.update_dist(b[1].predicted_distance(lat_me, lon_me), b)

                if not bus_not_passed(lat, lon, direction):
                    bus_pq.remove(bus)

        traffic_light_indicator(bus_pq, direction)
        keep_running -= 1
        time.sleep(freq_sec)


# EFFECTS: Encapsulates the logic for changing the lights
def traffic_light_indicator(buses: {}, direction: str) -> None:
    if buses.peek_min()[0] < 1000:
        # green light
        bridge.set_light(lr_lamp, 'xy', [0.2206, 0.662])
    else:
        # red light
        bridge.set_light(lr_lamp, 'xy', [0.6679, 0.2969])


# EFFECTS: Helper function to determine if
def bus_not_passed(lat: float, lon: float, direction: str) -> bool:
    if direction == 'westbound':
        result: bool = abs(lon) < abs(lon_me)
    elif direction == 'eastbound':
        result: bool = abs(lon) > abs(lon_me)
    elif direction == 'northbound':
        result: bool = abs(lat) < abs(lat_me)
    else:
        result: bool = abs(lat) > abs(lat_me)
    return result


bus_14_id = '16718'
bus_99_id = '6641'
run_buswatch(bus_14_id, 'westbound', 500, 40)

