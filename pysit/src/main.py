#!../venv/bin/python

"""
WITH DEBUGGER
1st (naive implementation without data structures for stop-times and trips):
    load_stop_times:    1889.3  ms
    req/sec:            1515    reqs (25.24/sec)

WITH DEBUGGER
2nd (exchanged ):
    load_stop_times:    3745.8  ms
    req/sec:            1667    reqs (27.7/sec) 

WITHOUT DEBUGGER
3rd (exchanged ):
    load_stop_times:    3683.3  ms
    req/sec:            4950    reqs (89.54/s) 


WITHOUT DEBUGGER
4th (exchanged ):
    load_stop_times:    3688.1  ms 
    req/sec:            1737    reqs (28.94/s) 

"""

import time 
from dataclasses import dataclass
from flask import Flask, Response
from flask import jsonify

from typing import List, Dict, Tuple


app = Flask(__name__)


FILES = {
    "TRIPS": "../../MBTA_GTFS/trips.txt",
    "STOP_FILES": "../../MBTA_GTFS/stop_times.txt"
}


class StopTime:
    def __init__(self, trip_id, arrival, departure, stop_id):
        self.trip_id = trip_id
        self.arrival = arrival
        self.departure = departure
        self.stop_id = stop_id


class Trip:
    def __init__(self, trip_id, route_id, service_id):
        self.trip_id = trip_id
        self.route_id = route_id
        self.service_id = service_id


class StopTimeResponse:
    def __init__(self, stop_id, arrival_time, departure_time):
        self.stop_id = stop_id
        self.arrival_time = arrival_time
        self.departure_time = departure_time
    
    def to_dict(self):
        return {
            "stop_id": self.stop_id,
            "arrival_time": self.arrival_time,
            "departure_time": self.departure_time
        }


class TripResponse:
    def __init__(self, trip_id, route_id, service_id, schedules):
        self.trip_id = trip_id
        self.route_id = route_id
        self.service_id = service_id
        self.schedules = schedules

    def to_dict(self):
        return {
            "trip_id": self.trip_id,
            "route_id": self.route_id,
            "service_id": self.service_id,
            "schedules": [schedule.to_dict() for schedule in self.schedules]
        }


class GTFS:
    trips = []
    trips_ix_by_route = {}
    stop_times = []
    stop_times_ix_by_trip = {}

    def __init__(self):
        self.trips, self.trips_ix_by_route = self._load_trips()
        self.stop_times, self.stop_times_ix_by_trip = self._load_stop_times()

    def schedule_for_route(self, route) -> List[TripResponse]:
        trips: List[TripResponse] = []
        trip_ixs = self.trips_ix_by_route.get(route)

        if (trip_ixs != None):
            for trip_ix in trip_ixs:
                trip = self.trips[trip_ix]
                stop_time_ixs = self.stop_times_ix_by_trip[trip.trip_id]
                schedules = []

                for stop_time_ix in stop_time_ixs:
                    stop_time = self.stop_times[stop_time_ix]
                    
                    schedules.append(StopTimeResponse(
                        stop_id=stop_time.stop_id, 
                        arrival_time=stop_time.arrival, 
                        departure_time=stop_time.departure)
                        )

                trips.append(TripResponse(
                    trip_id=trip.trip_id, 
                    route_id=trip.route_id, 
                    service_id=trip.service_id, 
                    schedules=schedules)
                    )

        return trips


    def _load_trips(self) -> Tuple[List[Trip], Dict[str, int]]:
        lines = ""
        with open(FILES["TRIPS"], "r") as trips:
            lines = trips.readlines()

        header = lines[0].split(",")
        print(header)
        assert header[0] == "route_id"
        assert header[1] == "service_id"
        assert header[2] == "trip_id"

        trips = []
        trips_ix_by_route = {}

        i = 0
        for line in lines[1:]:
            cells = line.split(",")
            route_id = cells[0]
            trips.append(Trip(trip_id=cells[2], route_id=route_id, service_id=cells[1]))

            if route_id in trips_ix_by_route:
                trips_ix_by_route[route_id].append(i)
            else:
                trips_ix_by_route[route_id] = [i]

            i += 1

        return (trips, trips_ix_by_route)


    def _load_stop_times(self) -> Tuple[List[StopTime], Dict[str, int]]:
        start_time = time.time()
        lines = ""
        with open(FILES["STOP_FILES"], "r") as stop_file:
            lines = stop_file.readlines()
            header = lines[0].split(",")
            assert header[0] == "trip_id"
            assert header[1] == "arrival_time"
            assert header[2] == "departure_time"
            assert header[3] == "stop_id"

            stop_times: List[StopTime] = []
            stop_times_ix_by_trips: Dict[str, int] = {}

            i = 0
            for line in lines[1:]:
                cells = line.split(",")
                trip_id = cells[0]
                stop_times.append(StopTime( trip_id=trip_id, arrival=cells[1], departure=cells[2], stop_id=cells[3]))

                if trip_id in stop_times_ix_by_trips:
                    stop_times_ix_by_trips[trip_id].append(i)
                else:
                    stop_times_ix_by_trips[trip_id] = [i]

                i += 1
            
        end_time = time.time()
        print(f"Elapsed time in seconds: {(end_time-start_time)*1000}")
        return (stop_times, stop_times_ix_by_trips)


gtfs = GTFS()


@app.route("/schedules/<route_id>", methods=["GET"])
def index(route_id) -> Response:
    trip_responses = gtfs.schedule_for_route(route_id) 
    trip_responses = [trip.to_dict() for trip in trip_responses] 

    content = jsonify(trip_responses)
    return content


if __name__ == "__main__":
    config = {
        "host": "127.0.0.1",
        "port": 4000,
        "debug": False
    }

    app.run(**config)
