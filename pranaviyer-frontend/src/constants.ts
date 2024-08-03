import { LatLngTuple } from "leaflet";

export type Location = {
  id: number;
  timestamp: Date;
  latitude: number;
  longitude: number;
  position_accuracy: number;
  altitude: number;
  altitude_accuracy: number;
  heading: number;
  speed: number;
};

export interface APILocation extends Omit<Location, "timestamp"> {
  timestamp: string;
}

export type Search = {
  id: number;
  timestamp: Date;
  text: string;
}

export interface APISearch extends Omit<Search, "timestamp"> {
  timestamp: string;
}

export const CENTER: LatLngTuple = [59.91705240606919, 10.74147640762516];
