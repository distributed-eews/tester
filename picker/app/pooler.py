from typing import Dict, List, Set
from datetime import datetime, timedelta

CHANNELS = ["BHE", "BHN", "BHZ"]


class Pooler:
    def __init__(self):
        self.data_points: Dict[str, Dict[str, List[int]]] = {}
        self.station_first_start_time: Dict[str, datetime] = {}
        self.station_data_count: Dict[str, int] = {}
        self.initiated_stations: Set[str] = set()
        self.station_p_time: Dict[str, datetime] = {}
        self.station_s_time: Dict[str, datetime] = {}
        self.cache: Dict[str, Dict[str, List[int]]] = {}

    def reset(self):
        self.data_points = {}
        self.station_first_start_time = {}
        self.station_data_count = {}
        self.initiated_stations = set()
        self.station_p_time = {}
        self.station_s_time = {}
        self.cache = {}

    def reset_ps(self, station: str):
        if station in self.cache:
            self.cache[station] = {}

        if station in self.station_p_time:
            self.station_p_time[station] = {}

        if station in self.station_s_time:
            self.station_s_time[station] = {}

        self.initiated_stations.remove(station)

    def print_ps_info(self, station: str):
        p_time = self.station_p_time.get(station, None)
        s_time = self.station_s_time.get(station, None)
        cache = self.cache.get(station, None)

    def set_cache(self, station: str, channel: str, data: List[int], extend=False):
        if station not in self.cache:
            self.cache[station] = {}

        if channel not in self.cache[station]:
            self.cache[station][channel] = []

        if not extend:
            self.cache[station][channel] = data
            return

        self.cache[station][channel].extend(data)

    def set_caches(self, station: str, data: List[List[int]], extend=False):
        for i in range(3):
            channel = CHANNELS[i]
            self.set_cache(station, channel, data[i], extend)

    def set_station_first_start_time(self, station: str, start_time: datetime):
        if not station in self.station_first_start_time:
            self.station_first_start_time[station] = start_time

    def extend_data_points(self, station: str, channel: str, data_points: List[int]):
        if not station in self.data_points:
            self.data_points[station] = {}

        if not channel in self.data_points[station]:
            self.data_points[station][channel] = []

        self.data_points[station][channel].extend(data_points)

    def is_ready_to_predict(self, station: str) -> bool:
        if not station in self.data_points:
            return False

        if len(self.data_points[station]) != 3:
            return False

        for channel in self.data_points[station]:
            if len(self.data_points[station][channel]) < 200:
                return False
        return True

    def is_ready_to_init(self, station: str) -> bool:
        if station in self.initiated_stations:
            return False

        if not station in self.data_points:
            return False

        if len(self.data_points[station]) != 3:
            return False

        for channel in self.data_points[station]:
            if len(self.data_points[station][channel]) < 382:
                return False
        return True

    def inc_station_data_count(self, station: str, count: int):
        if station not in self.station_data_count:
            self.station_data_count[station] = 0

        self.station_data_count[station] += count

    def get_station_time(self, station: str) -> datetime:
        now = datetime.utcnow()

        if not station in self.station_first_start_time:
            return now

        if not station in self.station_data_count:
            return now

        first_time = self.station_first_start_time[station]
        count = self.station_data_count[station]
        time_to_add = timedelta(seconds=count / 20)

        return time_to_add + first_time

    def get_data_to_predict(self, station: str) -> List[List[int]]:
        if not self.is_ready_to_predict(station):
            return []

        data = []

        # for channel in self.data_points[station]:
        for channel in CHANNELS:
            data_points = self.data_points[station][channel]
            data.append(data_points[:200])
            self.data_points[station][channel] = data_points[200:]

        self.inc_station_data_count(station, 200)

        return data

    def get_data_to_init(self, station: str) -> List[List[int]]:
        if not self.is_ready_to_init(station):
            return []

        data = []

        # for channel in self.data_points[station]:
        for channel in CHANNELS:
            data_points = self.data_points[station][channel]
            data.append(data_points[:382])
            self.data_points[station][channel] = data_points[382:]
            self.set_cache(station, channel, data_points[-200:])

        self.inc_station_data_count(station, 382)

        return data

    def get_cache(self, station: str):
        data = []
        if station not in self.cache:
            return data

        for channel in CHANNELS:
            data_points = self.cache[station][channel]
            data.append(data_points)
        return data

    def has_initiated(self, station: str) -> bool:
        return station in self.initiated_stations

    def add_initiated_station(self, station: str) -> None:
        self.initiated_stations.add(station)
