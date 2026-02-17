from dataclasses import dataclass
from typing import Any, Dict, List
import shapely
import geopandas
import pandas as pd
import numpy as np


def print_time(ts: pd.Timestamp) -> str:
    return ts.tz_convert("Europe/Brussels").strftime("%Y-%m-%d %H:%M:%S")


def get_centroid_latlon(gdf) -> shapely.Point:
    centroid = shapely.Point(gdf.geometry.x.mean(), gdf.geometry.y.mean())
    return geopandas.GeoSeries([centroid], crs=gdf.crs).to_crs("EPSG:4326")[0]


@dataclass
class Range:
    start: shapely.Point
    start_idx: int
    end: shapely.Point
    end_idx: int
    centroid: shapely.Point

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Range [{self.start_idx}-{self.end_idx}] (<{print_time(self.start.timestamp)}> - <{print_time(self.end.timestamp)}>)"

    def distance(self, other: "Range") -> float:
        if self.start_idx < other.end_idx:
            return other.distance(self)
        else:
            return self.start.geometry.distance(other.end.geometry)

    def merge(self, other: "Range") -> "Range":
        if self.start_idx < other.end_idx:
            return other.merge(self)
        else:
            self.start = other.start
            self.start_idx = other.start_idx
            return self

    def to_dict(self) -> Dict[str, Any]:
        start_time = self.start.timestamp.tz_convert("Europe/Brussels").isoformat()
        end_time = self.end.timestamp.tz_convert("Europe/Brussels").isoformat()
        return {
            "latitude": self.centroid.y,
            "longitude": self.centroid.x,
            "start_time": start_time,
            "end_time": end_time,
            "id": f"{start_time}-{end_time}",
        }


def get_stationary_ranges(gdf) -> List[Range]:
    THRESH = 2e1
    d = np.vstack([gdf.geometry.x, gdf.geometry.y])
    N = d.shape[1]
    i = 0
    min_ws = 5
    ranges = []
    while i < N - min_ws:
        for j in range(i + min_ws, N):
            if np.linalg.norm(np.std(d[:, i:j], axis=1)) > THRESH:
                dt = gdf.iloc[j - 1].timestamp - gdf.iloc[i].timestamp
                if dt > pd.Timedelta("7 minutes"):
                    rowI = gdf.iloc[i]
                    rowJ = gdf.iloc[j]
                    ranges.append(
                        Range(rowI, i, rowJ, j, get_centroid_latlon(gdf.iloc[i:j]))
                    )
                break
        else:
            dt = gdf.iloc[j - 1].timestamp - gdf.iloc[i].timestamp
            if dt > pd.Timedelta("7 minutes"):
                rowI = gdf.iloc[i]
                rowJ = gdf.iloc[j]
                ranges.append(
                    Range(rowI, i, rowJ, j, get_centroid_latlon(gdf.iloc[i:j]))
                )
            break
        i = j

    # merge ranges where previous ends very close to next's start
    for i in range(len(ranges) - 1, 1, -1):
        if ranges[i].distance(ranges[i - 1]) < 50:
            ranges[i - 1] = ranges[i].merge(ranges[i - 1])
            ranges.pop(i)
    return [r.to_dict() for r in ranges]
