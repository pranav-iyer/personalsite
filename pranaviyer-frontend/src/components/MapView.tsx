import { Circle, MapContainer, Polyline, TileLayer } from "react-leaflet";
import { CENTER, Range } from "../constants";

type Props = {
  ranges: Range[];
  highlightedRangeId: string | null;
};

const MapView = ({ ranges, highlightedRangeId }: Props) => {
  const highlightedRange = ranges
    .filter((rng) => rng.id === highlightedRangeId)
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
            color={"firebrick"}
          />
        ))}
      <Polyline
        positions={ranges.map((rng) => [rng.latitude, rng.longitude])}
        color="lightgray"
        dashArray={[2, 4]}
      />
      {highlightedRange && (
        <Circle
          center={[highlightedRange.latitude, highlightedRange.longitude]}
          radius={40}
          color="black"
        />
      )}
    </MapContainer>
  );
};
export default MapView;
