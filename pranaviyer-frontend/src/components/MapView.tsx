import { Circle, MapContainer, Polyline, TileLayer } from "react-leaflet";
import { CENTER, Location } from "../constants";

type Props = {
  locations: Location[];
  highlightedLocationId: number | null;
};

const MapView = ({ locations, highlightedLocationId }: Props) => {
  const highlightedLocation = locations
    .filter((loc) => loc.id === highlightedLocationId)
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
      <Polyline
        positions={locations.map((loc) => [loc.latitude, loc.longitude])}
        color="deepskyblue"
        dashArray={[2, 4]}
      />
      {highlightedLocation && (
        <Circle
          center={[highlightedLocation.latitude, highlightedLocation.longitude]}
          radius={highlightedLocation.position_accuracy}
          color="black"
        />
      )}
    </MapContainer>
  );
};
export default MapView

