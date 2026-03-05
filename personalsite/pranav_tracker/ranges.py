from dataclasses import dataclass
from typing import Any
import shapely
import geopandas
import pandas as pd
import numpy as np

HOME_TIMEZONE = "Europe/Brussels"
LATLON_CRS = "EPSG:4326"


def print_time(ts: pd.Timestamp) -> str:
    return ts.tz_convert(HOME_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def get_centroid_latlon(gdf) -> shapely.Point:
    centroid = shapely.Point(gdf.geometry.x.mean(), gdf.geometry.y.mean())
    return geopandas.GeoSeries([centroid], crs=gdf.crs).to_crs(LATLON_CRS)[0]


def get_centroid(gdf) -> shapely.Point:
    return shapely.Point(gdf.geometry.x.mean(), gdf.geometry.y.mean())


@dataclass
class Range:
    start_idx: int
    end_idx: int
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    centroid: shapely.Point
    centroid_latlon: shapely.Point

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Range (<{print_time(self.start_time)}> - <{print_time(self.end_time)}>) @ {self.centroid_latlon}"

    def distance(self, other: "Range") -> float:
        if self.start_time < other.end_time:
            return other.distance(self)
        else:
            return self.centroid.distance(other.centroid)

    def merge(self, other: "Range") -> "Range":
        if self.start_time < other.end_time:
            return other.merge(self)
        else:
            self.start_idx = other.start_idx
            self.start_time = other.start_time
            return self

    def to_dict(self) -> dict[str, Any]:
        start_time = self.start_time.tz_convert(HOME_TIMEZONE).isoformat()
        end_time = self.end_time.tz_convert(HOME_TIMEZONE).isoformat()
        return {
            "latitude": self.centroid_latlon.y,
            "longitude": self.centroid_latlon.x,
            "start_time": start_time,
            "end_time": end_time,
            "id": f"{start_time}-{end_time}",
        }


@dataclass
class Trip:
    start_idx: int
    end_idx: int
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    utm_coords: list[shapely.Point]
    latlons: list[shapely.Point]

    @property
    def average_velocity(self) -> float:
        dt = (self.end_time - self.start_time).total_seconds()
        dx = self.utm_coords[-1].distance(self.utm_coords[0])
        return 3.6 * dx / dt  # m/s to km/h

    def to_dict(self) -> dict[str, Any]:
        start_time = self.start_time.tz_convert(HOME_TIMEZONE).isoformat()
        end_time = self.end_time.tz_convert(HOME_TIMEZONE).isoformat()
        return {
            "start_time": start_time,
            "end_time": end_time,
            "id": f"{start_time}-{end_time}",
            "latlons": [{"latitude": p.y, "longitude": p.x} for p in self.latlons],
            "average_velocity": self.average_velocity,
        }


def get_trips(gdf: geopandas.GeoDataFrame, ranges: list[Range]) -> list[Trip]:
    trips: list[Trip] = []
    for i in range(len(ranges) - 1):
        start = ranges[i].end_idx + 1
        end = ranges[i + 1].start_idx - 1
        utm_coords = gdf.iloc[start : end + 1].geometry.to_list()
        latlon_coords = gdf.to_crs(LATLON_CRS).iloc[start : end + 1].geometry.to_list()
        trips.append(
            Trip(
                start,
                end,
                gdf.iloc[start].timestamp,
                gdf.iloc[end].timestamp,
                utm_coords,
                latlon_coords,
            )
        )
    return trips


def get_ranges_and_trips(
    gdf: geopandas.GeoDataFrame,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ranges = get_stationary_ranges(gdf)
    trips = get_trips(gdf, ranges)
    return [r.to_dict() for r in ranges], [t.to_dict() for t in trips]


def get_stationary_ranges(gdf) -> list[Range]:
    THRESH = 2e1
    d = np.vstack([gdf.geometry.x, gdf.geometry.y])
    N = d.shape[1]
    i = 0
    min_ws = 5
    ranges = []
    while i < N - min_ws:
        if np.linalg.norm(np.std(d[:, i : i + min_ws], axis=1)) > THRESH:
            # the first few points already have too large an stddev, i am likely moving
            i += 1
            continue
        for j in range(i + min_ws + 1, N):
            if np.linalg.norm(np.std(d[:, i:j], axis=1)) > THRESH:
                dt = gdf.iloc[j - 2].timestamp - gdf.iloc[i].timestamp
                if dt > pd.Timedelta("7 minutes"):
                    # ranges where i am stationary for less than 6 minutes i choose to treat as noise
                    ranges.append(
                        Range(
                            i,
                            j - 2,
                            gdf.iloc[i].timestamp,
                            # last stationary element is j-2 -- we've found i..j-1 to go above the threshold
                            gdf.iloc[j - 2].timestamp,
                            get_centroid(gdf.iloc[i : j - 1]),
                            get_centroid_latlon(gdf.iloc[i : j - 1]),
                        )
                    )
                break
        else:
            # we reached the end of the array without exceeding the threshold,
            # so the range i - N-1 is a stationary range
            dt = gdf.iloc[N - 1].timestamp - gdf.iloc[i].timestamp
            if dt > pd.Timedelta("3 minutes"):
                # at the end, the threshold is lower (3 minutes) because
                # if it's real-time data, might only get the tail end which could be quite short
                ranges.append(
                    Range(
                        i,
                        N - 1,
                        gdf.iloc[i].timestamp,
                        gdf.iloc[N - 1].timestamp,
                        get_centroid(gdf.iloc[i:]),
                        get_centroid_latlon(gdf.iloc[i:]),
                    )
                )
            break
        i = j - 1

    # merge ranges where previous ends very close to next's start
    for i in range(len(ranges) - 1, 0, -1):
        if ranges[i].distance(ranges[i - 1]) < 50:
            ranges[i - 1] = ranges[i].merge(ranges[i - 1])
            ranges.pop(i)

    return ranges
