import { Circle, MapContainer, Polyline, TileLayer } from "react-leaflet";
import { CENTER, Range, Trip } from "../constants";

type Props = {
  ranges: Range[];
  trips: Trip[];
  highlightedRangeId: string | null;
  highlightedTripId: string | null;
};

const MapView = ({
  ranges,
  trips,
  highlightedRangeId,
  highlightedTripId,
}: Props) => {
  const highlightedRange = ranges
    .filter((rng) => rng.id === highlightedRangeId)
    .at(0);
  const highlightedTrip = trips
    .filter((trip) => trip.id === highlightedTripId)
    .at(0);
  return (
    <MapContainer
      style={{ height: "calc(100vh - 175px)" }}
      center={CENTER}
      zoom={13}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />
      {ranges
        .filter((rng) => rng.id != highlightedRangeId)
        .map((rng) => (
          <Circle
            key={`${rng.start_time}-${rng.end_time}`}
            center={[rng.latitude, rng.longitude]}
            radius={30}
            color={"gray"}
          />
        ))}
      {highlightedRange && (
        <Circle
          center={[highlightedRange.latitude, highlightedRange.longitude]}
          radius={40}
          color="black"
        />
      )}
      {highlightedTrip && (
        <Polyline
          positions={highlightedTrip.latlons.map((latlon) => [
            latlon.latitude,
            latlon.longitude,
          ])}
          color="firebrick"
          dashArray={[2, 4]}
        />
      )}
    </MapContainer>
  );
};
export default MapView;
