import { useEffect, useRef } from "react";
import { Location, Search } from "../constants";
import * as d3 from "d3";

type Props = {
  locations: Location[];
  searches: Search[];
  viewDate: Date;
  highlightedLocation: number | null;
  setHighlightedLocation: (v: number | null) => void;
};

const HEIGHT = 500;

const Timeline = ({
  locations,
  searches,
  viewDate,
  highlightedLocation,
  setHighlightedLocation,
}: Props) => {
  const gY = useRef<SVGGElement | null>(null);
  const gDot = useRef<SVGGElement | null>(null);
  const gSearches = useRef<SVGGElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const startDT = new Date(viewDate.getTime());
  startDT.setHours(0);
  startDT.setMinutes(0);
  startDT.setSeconds(0);
  const endDT = new Date(viewDate.getTime());
  endDT.setHours(23);
  endDT.setMinutes(59);
  endDT.setSeconds(59);
  const y = d3.scaleTime().domain([startDT, endDT]).range([0, HEIGHT]);

  useEffect(() => {
    if (gY.current) {
      d3.select(gY.current).call(d3.axisLeft(y));
    }
  }, [y]);

  useEffect(() => {
    if (gDot.current) {
      d3.select(gDot.current)
        .selectAll("circle")
        .attr("r", 8)
        .attr("stroke-width", 2);
    }
  }, [locations]);

  const zoomed = ({ transform }: { transform: d3.ZoomTransform }) => {
    const zy = transform.rescaleY(y).interpolate(d3.interpolateRound);
    if (gY.current) {
      d3.select(gY.current).call(d3.axisLeft(zy));
    }
    const dotTransform = new d3.ZoomTransform(transform.k, 0, transform.y);
    if (gDot.current) {
      d3.select(gDot.current)
        .attr("transform", dotTransform)
        .selectAll("circle")
        .attr("r", 6 / dotTransform.k)
        .attr("stroke-width", 2 / dotTransform.k);
    }
    if (gSearches.current) {
      d3.select(gSearches.current)
        .attr("transform", dotTransform)
        .style("font-size", 24 / transform.k);
    }
  };

  useEffect(() => {
    if (svgRef.current) {
      d3.select(svgRef.current).call(
        d3
          .zoom()
          .translateExtent([
            [0, -HEIGHT],
            [0, 2*HEIGHT],
          ])
          .on("zoom", zoomed),
      );
    }
  }, [svgRef]);

  return (
    <div className="col-2 col-md-1" id="timeline">
      <svg
        ref={svgRef}
        width="100%"
        height="calc(100vh - 90px)"
        viewBox={`-40 0 60 ${HEIGHT}`}
      >
        <g ref={gY} />
        <g ref={gDot} stroke="deepskyblue" fill="lightblue">
          {locations.map((loc) => (
            <circle
              onPointerEnter={() => setHighlightedLocation(loc.id)}
              onPointerLeave={() =>
                highlightedLocation === loc.id && setHighlightedLocation(null)
              }
              stroke={highlightedLocation === loc.id ? "darkblue" : undefined}
              key={loc.id}
              cx={0}
              cy={y(loc.timestamp)}
              style={{ cursor: "pointer" }}
            />
          ))}
        </g>
        <g ref={gSearches}>
          {searches.map((search) => (
            <text
              id={`search-icon-${search.id}`}
              key={search.id}
              x={0}
              y={y(search.timestamp)}
              fontWeight="bolder"
              onPointerEnter={() => {
                const bounds = document
                  .getElementById(`search-icon-${search.id}`)!
                  .getBoundingClientRect();
                d3.select("#tooltip")
                  .style("visibility", "visible")
                  .style("right", window.innerWidth - bounds.x - 12 + "px")
                  .style("top", bounds.y + "px")
                  .text(search.text);
              }}
              onPointerLeave={() => {
                d3.select("#tooltip")
                  .style("visibility", "hidden")
                  .text(search.text);
              }}
              style={{ cursor: "pointer" }}
            >
              &nbsp;&nbsp;?
            </text>
          ))}
        </g>
      </svg>
      <div
        id="tooltip"
        style={{
          position: "absolute",
          visibility: "hidden",
          zIndex: 999,
        }}
        className="shadow border border-dark bg-light rounded p-2"
      ></div>
    </div>
  );
};

export default Timeline;
