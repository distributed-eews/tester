from typing import Any
import redis
import json


class MyRedis:
    def __init__(self, config: dict[str, Any]):
        self.c = redis.Redis(**config, decode_responses=True)

    def get_nearest_stations(self, station: str) -> list[str]:
        n = self.c.get(f'NEAREST_STATION_{station}')
        if n is None or n == "":
            return []
        return n.split(",")

    def has_2_or_more_nearest_stations(self, station: str) -> bool:
        n = self.get_nearest_stations(station)
        return len(n) >= 2

    def save_waveform(self, station: str, waveform: dict):
        self.c.set(f"WAVEFORM_{station}", json.dumps(waveform), 60 * 10)

    def get_waveform(self, station: str) -> dict | None:
        r = self.c.get(f"WAVEFORM_{station}")
        if r is None:
            return None
        return json.loads(r)

    def has_3_waveform(self, station: str) -> bool:
        nearest_stats = self.get_nearest_stations(station)
        has_2_nearest = len(nearest_stats) >= 2
        if not has_2_nearest:
            return False

        nearest_stats.extend([station])
        i = 0
        for stat in nearest_stats:
            r = self.get_waveform(stat)
            if r is not None:
                i +=1
        print("has waveform: ", i)
        return i >= 3

    def get_loc(self, station: str):
        loc = self.c.get(f"LOCATION_{station}")
        if loc is None:
            return None
        loc = loc.split(";")
        loc = [float(l) for l in loc]
        return loc
    
    def get_3_waveform(self, station: str):
        print("get_3_waveform")
        nearest_stats = self.get_nearest_stations(station)
        nearest_stats.extend([station])
        for st in nearest_stats:
            data = self._get_3_waveform(st)
            if data is not None and len(data) >= 3:
                d = data[:3]
                print(d)
                return d
        return None

    def _get_3_waveform(self, station: str):
        if not self.has_3_waveform(station):
            print("No 3 waveform found")
            return None
        nearest_stats = self.get_nearest_stations(station)
        nearest_stats.extend([station])
        print(nearest_stats)

        data = []
        for stat in nearest_stats:
            wf = self.get_waveform(stat)
            loc = self.get_loc(stat)
            if (wf is None) or (loc is None) or (len(data) >= 3):
                continue
            wf["location"] = loc
            wf["distance"] = float(wf["distance"])
            data.append(wf)
        print("data wfs")
        if len(data) < 3:
            print("Data wfs not enough")
            return []
        return data

    def remove_3_waveform(self, stations: list[str]) -> None:
        for station in stations:
            self.c.delete(station)

    def remove_3_waveform_dict(self, wfs: list[dict[str]]) -> None:
        for wf in wfs:
            station = wf["station_code"]
            self.c.delete(f"WAVEFORM_{station}")
