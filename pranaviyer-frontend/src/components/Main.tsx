import { useQuery } from "@tanstack/react-query";
import MapView from "./MapView";
import { useRef, useState } from "react";
import { APIRange, APISearch, Range, Search } from "../constants";
import Timeline from "./Timeline";
import { formatDelta } from "../times";

const Main = () => {
  const [viewDate, setViewDate] = useState<Date | null>(new Date());
  const [highlightedRangeId, setHighlightedRangeId] = useState<string | null>(
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
    queryFn: async (): Promise<Range[]> => {
      if (!viewDate) return [];
      const response = await fetch(
        `/pranav-tracker/api/ranges/?view_date=${viewDate.toISOString().substring(0, 10)}`,
      );
      const ranges = await response.json();
      return ranges
        ? ranges.ranges.map((rng: APIRange) => ({
            ...rng,
            start_time: new Date(rng.start_time),
            end_time: new Date(rng.end_time),
          }))
        : [];
    },
  });
  const ranges = rangesQuery.data || [];
  const searches = searchesQuery.data || [];
  const highlightedRange = ranges
    .filter((rng) => rng.id === highlightedRangeId)
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
              <div className="col-4 col-lg-2">
                <input
                  type="date"
                  name="view_date"
                  defaultValue={new Date().toISOString().substring(0, 10)}
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
                ) : (
                  ""
                )}
              </div>
            </div>
          </div>
          <div className="row">
            <MapView highlightedRangeId={highlightedRangeId} ranges={ranges} />
          </div>
        </div>
        {viewDate && (
          <Timeline
            ranges={ranges}
            searches={searches}
            viewDate={viewDate}
            setHighlightedRangeId={setHighlightedRangeId}
          />
        )}
      </div>
    </>
  );
};

export default Main;
