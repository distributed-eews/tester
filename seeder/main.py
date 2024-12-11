import redis
import json
import os
import math
import copy
import random
from dotenv import load_dotenv

load_dotenv()

TRESHOLD_DISTANCE = int(os.environ.get("TRESHOLD_DISTANCE", "1000"))
REPLICAS = int(os.environ.get("REPLICAS", 1))


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance


def save_to_redis():
    host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = os.environ.get("REDIS_PORT", "6379")
    redis_password = os.environ.get("REDIS_PASSWORD", None)
    env = os.environ.get("ENV", "PROD")
    print(f"ENVIRONMENT: {env}")
    print(f"REDIS_HOST: {host}")

    # Dapatkan absolute path ke data.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_json_path = os.path.join(current_dir, "data.json")
    r = redis.Redis(
        host=host,
        port=int(redis_port),
        password=redis_password,
        db=0,
        decode_responses=True,
    )
    print(f"DATA JSON: {data_json_path}")
    with open(data_json_path, "r") as json_file:
        data = json_file.read()

    parsed: list = json.loads(data)
    station_codes = [stat["code"] for stat in parsed]
    r.set("ENABLED_STATION_CODES", ",".join(station_codes))

    replica_stats = []

    if env == "TEST":
        for stat in parsed:
            code = stat["code"]
            lat = float(stat["lat"])
            long = float(stat["long"])
            for j in range(REPLICAS):
                repl_stat = copy.deepcopy(stat)
                repl_stat["code"] = f"{code}-{j}"
                repl_stat["lat"] = str(round(random.uniform(lat - 7, lat + 7), 4))
                repl_stat["long"] = str(round(random.uniform(long - 7, long + 7), 4))
                replica_stats.append(repl_stat)
        parsed.extend(replica_stats)
    r.set("STATIONS", json.dumps(parsed))

    nearest_station_codes: dict[str, list[str]] = {}

    for stat1 in parsed:
        stat1_code = stat1["code"]
        lat1, lon1 = stat1["lat"], stat1["long"]
        nearest_station_codes[stat1_code] = []
        r.set(f"LOCATION_{stat1_code}", f"{lat1};{lon1}")
        loc = r.get(f"LOCATION_{stat1_code}").split(";")
        loc = [float(l) for l in loc]
        print(f"LOCATION {stat1_code}: {loc}")

        # Iterate through other stations and find the nearest 3
        nearest_stations = []
        for stat2 in parsed:
            stat2_code = stat2["code"]
            if stat1_code == stat2_code:
                continue

            lat2, lon2 = stat2["lat"], stat2["long"]
            distance = haversine(float(lat1), float(lon1), float(lat2), float(lon2))
            if distance > TRESHOLD_DISTANCE:
                continue

            if len(nearest_stations) < 10:
                # Append if there are less than 3 nearest stations
                nearest_stations.append((stat2_code, distance))
            else:
                # Replace farthest station if new distance is closer
                farthest_station = max(nearest_stations, key=lambda x: x[1])
                if distance < farthest_station[1]:
                    nearest_stations.remove(farthest_station)
                    nearest_stations.append((stat2_code, distance))

        # Sort nearest stations by distance
        nearest_station_codes[stat1_code] = [
            code for code, _ in sorted(nearest_stations)
        ]

    for key, value in nearest_station_codes.items():
        r.set(f"NEAREST_STATION_{key}", ",".join(value))
        print(f'Station: {key} : {",".join(value)}')

    print("Data saved to redis")


if __name__ == "__main__":
    save_to_redis()
