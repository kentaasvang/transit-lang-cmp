#!../venv/bin/python

import time 
from dataclasses import dataclass
from flask import Flask
from flask import render_template_string


app = Flask(__name__)


FILES = {
    "TRIPS": "../../MBTA_GTFS/trips.txt",
    "STOP_FILES": "../../MBTA_GTFS/stop_times.txt"
}


@dataclass
class StopTime:
    trip_id: str
    arrival: str
    departure: str
    stop_id: str


@dataclass
class Trip:
    trip_id: str
    route_id: str
    service_id: str


class GTFS:

    trips = []
    trips_ix_by_route = {}
    stop_times = []
    stop_times_ix_by_trip = {}

    def __init__(self):
        self.trips, self.trips_ix_by_route = self._load_trips()
        self.stop_times, self.stop_times_ix_by_trip = self._load_stop_times()

    def schedule_for_route(self, route):
        trips = []
        trip_ixs = self.trips_ix_by_route.get(route)
        if (trip_ixs != None):
            for trip_ix in trip_ixs:
                trip = self.trips[trip_ix]
                stop_time_ixs = self.stop_times_ix_by_trip[trip[0]]
                schedules = []
                for stop_time_ix in stop_time_ixs:
                    stop_time = self.stop_times[stop_time_ix]
                    schedules.append((stop_time[3], stop_time[1], stop_time[2]))

                trips.append((trip[2], trip[0], trip[1], schedules))

        return trips


    def _load_trips(self):
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
            # trip_id, route_id, service_id
            trips.append((cells[2], route_id, cells[1]))

            if route_id in trips_ix_by_route:
                trips_ix_by_route[route_id].append(i)
            else:
                trips_ix_by_route[route_id] = [i]

            i += 1

        return (trips, trips_ix_by_route)


    def _load_stop_times(self):
        start_time = time.time()
        lines = ""
        with open(FILES["STOP_FILES"], "r") as stop_file:
            lines = stop_file.readlines()
            header = lines[0].split(",")
            assert header[0] == "trip_id"
            assert header[1] == "arrival_time"
            assert header[2] == "departure_time"
            assert header[3] == "stop_id"

            stop_times = []
            stop_times_ix_by_trips = {}

            i = 0
            for line in lines[1:]:
                cells = line.split(",")
                trip_id = cells[0]
                stop_times.append((trip_id, cells[3], cells[1], cells[2]))

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
def index(route_id):
    return gtfs.schedule_for_route(route_id)


if __name__ == "__main__":
    config = {
        "host": "127.0.0.1",
        "port": 4000,
        "debug": True
    }

    app.run(**config)
