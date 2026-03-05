import { LatLngTuple } from "leaflet";

export type Search = {
  id: number;
  timestamp: Date;
  text: string;
};

export interface APISearch extends Omit<Search, "timestamp"> {
  timestamp: string;
}

export type Range = {
  id: string;
  start_time: Date;
  end_time: Date;
  latitude: number;
  longitude: number;
};

export interface APIRange extends Omit<Range, "start_time" | "end_time"> {
  start_time: string;
  end_time: string;
}

type LatLon = {
  latitude: number;
  longitude: number;
}

export type Trip = {
  id: string;
  start_time: Date;
  end_time: Date;
  average_velocity: number;
  latlons: LatLon[];
};

export interface APITrip extends Omit<Trip, "start_time" | "end_time"> {
  start_time: string;
  end_time: string;
}

export type RangesAndTrips = {
  ranges: Range[];
  trips: Trip[];
}
// export const CENTER: LatLngTuple = [59.91705240606919, 10.74147640762516]; // Oslo
export const CENTER: LatLngTuple = [50.876073, 4.700443]; // Leuven
