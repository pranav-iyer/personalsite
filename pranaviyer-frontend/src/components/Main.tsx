import { useQuery } from "@tanstack/react-query";
import MapView from "./MapView";
import { useRef, useState } from "react";
import {
  APIRange,
  APISearch,
  APITrip,
  RangesAndTrips,
  Search,
} from "../constants";
import Timeline from "./Timeline";
import { addDays, formatDelta } from "../times";

const Main = () => {
  const [viewDate, setViewDate] = useState<Date | null>(new Date());
  const [highlightedRangeId, setHighlightedRangeId] = useState<string | null>(
    null,
  );
  const [highlightedTripId, setHighlightedTripId] = useState<string | null>(
    null,
  );
  const dateInputRef = useRef<HTMLInputElement | null>(null);
  const searchesQuery = useQuery({
    queryKey: ["searches", viewDate],
    queryFn: async (): Promise<Search[]> => {
      if (!viewDate) return [];
      const response = await fetch(
        `/search/api/searches/?view_date=${viewDate.toISOString().substring(0, 10)}`,
      );
      const searches = await response.json();
      return searches
        ? searches.map((search: APISearch) => ({
            ...search,
            timestamp: new Date(search.timestamp),
          }))
        : [];
    },
  });
  const rangesQuery = useQuery({
    queryKey: ["ranges", viewDate],
    queryFn: async (): Promise<RangesAndTrips> => {
      if (!viewDate) return { ranges: [], trips: [] };
      const response = await fetch(
        `/pranav-tracker/api/ranges/?view_date=${viewDate.toISOString().substring(0, 10)}`,
      );
      const result = await response.json();
      return result
        ? {
            ranges: result.ranges.map((rng: APIRange) => ({
              ...rng,
              start_time: new Date(rng.start_time),
              end_time: new Date(rng.end_time),
            })),
            trips: result.trips.map((trip: APITrip) => ({
              ...trip,
              start_time: new Date(trip.start_time),
              end_time: new Date(trip.end_time),
            })),
          }
        : { ranges: [], trips: [] };
    },
  });
  const ranges = rangesQuery.data?.ranges || [];
  const trips = rangesQuery.data?.trips || [];
  const searches = searchesQuery.data || [];
  const highlightedRange = ranges
    .filter((rng) => rng.id === highlightedRangeId)
    .at(0);
  const highlightedTrip = trips
    .filter((trip) => trip.id === highlightedTripId)
    .at(0);
  const dateTimeFormat = new Intl.DateTimeFormat("en", {
    hour: "numeric",
    minute: "numeric",
  });
  return (
    <>
      <div className="row">
        <div className="col-10 col-md-11">
          <h2>Pranav Tracker</h2>
          <div className="row align-items-center mb-2">
            <div className="row align-items-center">
              <div className="col-5 col-lg-3 d-flex gap-1">
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => {
                    setViewDate((viewDate) => {
                      if (!viewDate) return null;
                      let yesterday = addDays(viewDate, -1);
                      if (dateInputRef.current)
                        dateInputRef.current.value = yesterday
                          .toISOString()
                          .substring(0, 10);
                      return yesterday;
                    });
                  }}
                >
                  &lt;
                </button>
                <input
                  type="date"
                  name="view_date"
                  defaultValue={new Date().toISOString().substring(0, 10)}
                  ref={dateInputRef}
                  className="form-control form-control-sm form-control-inline"
                  id="id_view_date"
                />
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => {
                    setViewDate((viewDate) => {
                      if (!viewDate) return null;
                      let tomorrow = addDays(viewDate, 1);
                      if (dateInputRef.current)
                        dateInputRef.current.value = tomorrow
                          .toISOString()
                          .substring(0, 10);
                      return tomorrow;
                    });
                  }}
                >
                  &gt;
                </button>
              </div>
              <div className="col-3 col-lg-1">
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
              <div className="col-2 col-lg-4 text-end p-0">
                {highlightedRange ? (
                  <>
                    {formatDelta(
                      highlightedRange.start_time,
                      highlightedRange.end_time,
                    )}{" "}
                    (
                    {dateTimeFormat.formatRange(
                      highlightedRange.start_time,
                      highlightedRange.end_time,
                    )}
                    )
                  </>
                ) : highlightedTrip ? (
                  <>
                    {formatDelta(
                      highlightedTrip.start_time,
                      highlightedTrip.end_time,
                    )}{" "}
                    (
                    {dateTimeFormat.formatRange(
                      highlightedTrip.start_time,
                      highlightedTrip.end_time,
                    )}
                    ) - 
                    Avg. speed:{" "}
                    {highlightedTrip.average_velocity.toPrecision(2)} km/h
                  </>
                ) : (
                  ""
                )}
              </div>
            </div>
          </div>
          <div className="row">
            <MapView
              highlightedRangeId={highlightedRangeId}
              highlightedTripId={highlightedTripId}
              ranges={ranges}
              trips={trips}
            />
          </div>
        </div>
        {viewDate && (
          <Timeline
            ranges={ranges}
            trips={trips}
            searches={searches}
            viewDate={viewDate}
            setHighlightedRangeId={setHighlightedRangeId}
            setHighlightedTripId={setHighlightedTripId}
          />
        )}
      </div>
    </>
  );
};

export default Main;
