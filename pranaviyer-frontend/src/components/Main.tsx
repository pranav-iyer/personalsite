import { useQuery } from "@tanstack/react-query";
import MapView from "./MapView";
import { useRef, useState } from "react";
import { APILocation, Location } from "../constants";
import Timeline from "./Timeline";

const Main = () => {
  const [viewDate, setViewDate] = useState<Date | null>(new Date("2024-07-25"));
  const [highlightedLocationId, setHighlightedLocationId] = useState<number | null>(
    null,
  );
  const dateInputRef = useRef<HTMLInputElement | null>(null);
  const query = useQuery({
    queryKey: ["locations", viewDate],
    queryFn: async (): Promise<Location[]> => {
      if (!viewDate) return [];
      const response = await fetch(
        `/pranav-tracker/api/locations/?view_date=${viewDate.toISOString().substring(0, 10)}`,
      );
      const locations = await response.json();
      return locations
        ? locations.map((loc: APILocation) => ({
          ...loc,
          timestamp: new Date(loc.timestamp),
        }))
        : [];
    },
  });
  const locations = query.data || [];
  return (
    <>
      <div className="row align-items-center mb-2">
        <div className="row align-items-center">
          <div className="col-4 col-lg-2">
            <input
              type="date"
              name="view_date"
              defaultValue={"2024-07-25"}
              ref={dateInputRef}
              className="form-control form-control-sm form-control-inline"
              id="id_view_date"
            />
          </div>
          <div className="col-4 col-lg-2">
            <button
              className="btn btn-sm btn-primary"
              onClick={() =>
                dateInputRef.current &&
                setViewDate(new Date(dateInputRef.current.value))
              }
            >
              Search
            </button>
          </div>
          <div className="col-4 col-lg-8 text-end p-0">
            ({locations.length} locations)
          </div>
        </div>
      </div>
      <div className="row">
        <MapView locations={locations} highlightedLocationId={highlightedLocationId} />
        {viewDate && (
          <Timeline
            locations={locations}
            viewDate={viewDate}
            highlightedLocation={highlightedLocationId}
            setHighlightedLocation={setHighlightedLocationId}
          />
        )}
      </div>
    </>
  );
};

export default Main;
