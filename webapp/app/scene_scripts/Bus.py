from .helpers import haversine_dist
from datetime import datetime, timedelta
from collections import deque

"""

"""


class _GpsPoint:  # leading underscore is PEP8 for inner classes
    """
    Parameters
    -------------
    lat : double
    lon : double
    gps_time : datetime
    """

    def __init__(self, lat: float, lon: float, gps_time: datetime):
        self.lat = lat
        self.lon = lon
        self.gps_time = gps_time

    # EFFECTS: override equals
    def __eq__(self, other):
        return self.gps_time == other.gps_time


class Bus:
    """
    Member fields
    ----------------
    gps_points : queue of GpsPoint
    vehicle_id : the vehicle ID of the bus
    route_id : the route ID of the bus, different than the rider facing route number
    """
    MAX_GPS_POINTS = 3

    def __init__(self, vehicle_id: str, route_id: str):
        self.gps_points = deque()
        self.vehicle_id = vehicle_id
        self.route_id = route_id

    # EFFECTS: adds a GPS point (lat, lon, gps_time, seconds since last check-in) to the array gps_points
    def add_gps_point(self, lat: float, lon: float, time: datetime) -> None:
        gps_point = _GpsPoint(lat, lon, time)
        if gps_point not in self.gps_points:
            self.gps_points.append(gps_point)
        if len(self.gps_points) > self.MAX_GPS_POINTS:
            self.gps_points.popleft()  # pop the oldest element off so we are only using the 3 most recent points

    def lk_pos(self) -> (int, int):
        return self.gps_points[0]

    # REQUIRES: at least two points in gps_points, max of MAX_GPS_POINTS.
    # EFFECTS: Calculates the naive average speed given the last three unique GPS positions and their times
    def gps_bus_speed(self) -> float:
        # TODO: Test this nonsense. Have sanity checks for speeds
        if len(self.gps_points) > 1:
            dist_diff = haversine_dist(self.gps_points[0].lat, self.gps_points[0].lon,
                                       self.gps_points[len(self.gps_points) - 1].lat,
                                       self.gps_points[len(self.gps_points) - 1].lon)
            time_diff = abs(self.gps_points[0].gps_time - self.gps_points[len(self.gps_points) - 1].gps_time)
            # mean speed in m/s
            return dist_diff / time_diff.total_seconds()

    # EFFECTS: linear prediction of location based on calculated average speed
    def predicted_distance(self, lat: float, lon: float) -> float:
        if len(self.gps_points) > 1:
            speed = self.gps_bus_speed()
            time_delta = (datetime.now() - self.lk_pos().gps_time).total_seconds()
            gps_dist = haversine_dist(self.lk_pos().lat, self.lk_pos().lon, lat, lon)
            return gps_dist - (speed * time_delta)
        else:
            return haversine_dist(self.lk_pos().lat, self.lk_pos().lon, lat, lon)

    # EFFECTS: override equals
    def __eq__(self, other):
        return self.vehicle_id == other.vehicle_id and self.route_id == other.route_id

    # EFFECTS: overrides __hash__ to make Bus hashable
    def __hash__(self):
        return hash((self.vehicle_id, self.route_id))

    '''
        When using a tuple, heapq will sort based on the first element BUT 
        tuple comparison breaks for (priority, task) pairs if the priorities 
        are equal and the tasks do not have a default comparison order. Bus implements
        __lt__ and __gt__ to both return false so that there is no inherent ordering
    '''

    # EFFECTS: Override lt comparator for use in priority queues.
    #          Simply returns False for now as there is no inherent ordering for a bus.
    #          This is a workaround for heapq using tuples [see heapq documentation]
    def __lt__(self, other):
        return False

    # EFFECTS: Override gt comparator for use in priority queues.
    #          Simply returns False for now as there is no inherent ordering for a bus.
    #          This is a workaround for heapq using tuples [see heapq documentation]
    def __gt__(self, other):
        return False

