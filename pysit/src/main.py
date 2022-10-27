#!./venv/bin/python
import time 
from dataclasses import dataclass
from flask import Flask
from flask import render_template_string


app = Flask(__name__)


FILES = {
    "TRIPS": "../../MBTA_GTFS/trips.txt",
    "STOP_FILES": "../../MBTA_GTFS/stop_times.txt"
}


@app.route("/schedules/<route_id>", methods=["GET"])
def index(route_id):
    return f"{load_trips()}"


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


def load_trips():
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
        trips.append(Trip(cells[2], route_id, cells[1]))

        if route_id in trips_ix_by_route:
            trips_ix_by_route[route_id].append(i)
        else:
            trips_ix_by_route[route_id] = [i]

        i += 1

    return (trips, trips_ix_by_route)


def load_stop_times():
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

            if trip_id in stop_times_ix_by_trips:
                stop_times_ix_by_trips[trip_id].append(i)
            else:
                stop_times_ix_by_trips[trip_id] = [i]

            i += 1
        
        end_time = time.time()
        print(f"Elapsed time in seconds: {end_time-start_time}")
        return (stop_times, stop_times_ix_by_trips)


    pass


if __name__ == "__main__":
    config = {
        "host": "127.0.0.1",
        "port": 4000,
        "debug": True
    }

    app.run(**config)
