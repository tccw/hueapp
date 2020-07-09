import os
import sys
import dotenv
from math import asin, sin, cos, sqrt, radians
from time import sleep

import urllib.request
import urllib.response
#import osrm

from datetime import datetime, timedelta
from google.transit import gtfs_realtime_pb2
from phue import Bridge
from scene_scripts.helpers import load_file

dotenv.load_dotenv(dotenv.find_dotenv())

"""
Route and arrival data used in this product or service is provided by permission of TransLink. 
TransLink assumes no responsibility for the accuracy or currency of the Data used in this product or service.
"""


# Class definition
class Bus:

    def __init__(self, vehicle_id, route_id):
        self.gps_points = []
        self.vehicle_id = vehicle_id
        self.route_id = route_id
        # self.dist_from_me = dist_from_me

    # TODO: store the last two unique GPS points and calculate the speed of the bus to forward prop the position
    #       Use the timestamp field to determine if the GPS point is unique.
    # EFFECTS: adds a GPS point (lat, lon, gps_time, seconds since last check-in) to the array gps_points
    def add_gps_point(self, gps_point):
        if gps_point not in self.gps_points:
            self.gps_points.append(gps_point)
            print("ADDED GPS POINT: to " + self.vehicle_id)

    # REQUIRES: a list of valid latitude, longitude, and time tuples. The list should be of length three.
    # EFFECTS: Calculates the naive average speed given the last three unique GPS positions and their times
    def gps_bus_speed(self):
        # data [(lat, lon, datetime), (lat, lon, datetime), (lat, lon, gps_time, seconds since last check-in)]
        dist_list = []
        time = []
        for g in self.gps_points:
            dist_list.append(haversine_dist(g.lat, g.lon, lat_me, lon_me))
            time.append(g.gps_time)

        # TODO: Test this nonsense. Fix so that only unique GPS points get added. Have sanity checks for speeds
        dist_diff_list = [dist_list[i + 1] - dist_list[i] for i in range(len(dist_list) - 1)]
        time_diff_list = [time[i + 1] - time[i] for i in range(len(time) - 1)]
        time_diff_list = [dt.total_seconds() for dt in time_diff_list]

        # mean speed in m/s
        return sum(dist_diff_list) / sum(time_diff_list)

    # EFFECTS: override equals
    def __eq__(self, other):
        return self.vehicle_id == other.vehicle_id


class GpsPoint:
    """
    Parameters
    -------------
    lat : double
    lon : double
    gps_time : datetime
    """

    def __init__(self, lat, lon, gps_time):
        self.lat = lat
        self.lon = lon
        self.gps_time = gps_time

    # EFFECTS: override equals
    def __eq__(self, other):
        return (self.lat == other.lat) & (self.lon == other.lon)


# Function definitions
# TODO: check initial Earth radius estimate. Differences are too high between this function and more precise
#       iterative solutions.
def haversine_dist(lat1, lon1, lat2, lon2):
    """
    http://www.faqs.org/faqs/geography/infosystems-faq/
    Haversine Formula (from R.W. Sinnott, "Virtues of the Haversine",
     Sky and Telescope, vol. 68, no. 2, 1984, p. 159)
    """
    phi_1 = radians(lat1)
    phi_2 = radians(lat2)
    lambda_1 = radians(lon1)
    lambda_2 = radians(lon2)

    r = 6378 - 21 * sin(phi_2)  # Radius of the Earth crude latitude adjustment (in km)

    term_1 = (sin((phi_2 - phi_1) / 2)) ** 2
    term_2 = cos(lat1) * cos(phi_2) * (sin((lambda_2 - lambda_1) / 2)) ** 2
    hav_term = 2 * asin(sqrt(term_1 + term_2))  # distance in radians

    distance_km = r * hav_term
    distance_m = round(distance_km * 1000, 0)
    return distance_m


# Constants
#file = "/scene_scripts/data/my_location.txt"
#path = os.getcwd() + file
#data = load_file(path)
lat_me = float(os.getenv('MYLAT'))
lon_me = float(os.getenv('MYLON'))
API_KEY = os.getenv('API_KEY')
bridge_ip = os.getenv('BRIDGE_IP')
westbound = 1
eastbound = 0
lights_flag = False

if lights_flag:
    # connect to the bridge
    b = Bridge(bridge_ip)
    b.connect()
    # create a light grouping and turn them on
    lr_lamp = [1]
    command = {'on': True, 'bri': 127}
    b.set_light(lr_lamp, command)
    # print(b.get_api())

bus_list = []
for n in range(500):
    feed = gtfs_realtime_pb2.FeedMessage()
    response = urllib.request.urlopen('https://gtfs.translink.ca/v2/gtfsposition?apikey=' + API_KEY)
    feed.ParseFromString(response.read())
    green_dist = []
    red_dist = []

    for entity in feed.entity:
        if (entity.HasField('vehicle') and
                (entity.vehicle.trip.route_id == "16718") and
                (entity.vehicle.trip.direction_id == westbound)):
            # print(entity)

            lat_1 = entity.vehicle.position.latitude
            lon_1 = entity.vehicle.position.longitude

            busID = entity.vehicle.vehicle.id
            now = datetime.now()
            bus_checkin_time = datetime.fromtimestamp(int(entity.vehicle.timestamp))
            time_diff = now - bus_checkin_time

            bus = Bus(busID, entity.vehicle.trip.route_id)
            if not bus_list:
                bus_list.append(bus)
                bus.add_gps_point(GpsPoint(lat_1, lon_1, bus_checkin_time))
            elif bus in bus_list:
                for b in bus_list:
                    if bus == b:
                        b.add_gps_point(GpsPoint(lat_1, lon_1, bus_checkin_time))
                        break
            else:
                bus_list.append(bus)
                bus.add_gps_point(GpsPoint(lat_1, lon_1, bus_checkin_time))

            dist_meters = haversine_dist(lat_1, lon_1, lat_me, lon_me)
            # TODO: set light color logic using traffic light system.
            # TODO: incorporate RTTI as GPS data might not be frequent enough to be reliable at this scale of prediction
            if ((lon_1 > lon_me) and
                    (dist_meters < 1300) and
                    (dist_meters > 500) and
                    (time_diff < timedelta(seconds=90))):
                green_dist.append(dist_meters)
            # print("A westbound 14 is close! Leave now!")
            if lon_1 > lon_me:
                print(
                    f'The 14 bus with ID {busID} is {dist_meters} meters away.\n'
                    f'GPS-data received {round(time_diff.total_seconds(), 0)} seconds ago.\n'
                )
            for b in bus_list:
                if len(b.gps_points) >= 3:
                    print(
                        f'The average speed of {b.vehicle_id} is {round(b.gps_bus_speed() * 3.6, 0)} km/r'
                    )

    print('------------------------------------------------------------------------')
    if lights_flag:
        if not len(green_dist):
            b.set_light(lr_lamp, 'xy', [0.6679, 0.2969])
            print('turn red')
        else:
            b.set_light(lr_lamp, 'xy', [0.2206, 0.662])
            print('turn green')

            print('------------------------------------------------------------------------')

    sleep(20)
