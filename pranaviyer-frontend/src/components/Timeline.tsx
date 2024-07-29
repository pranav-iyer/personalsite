import { useEffect, useRef, useState } from "react";
import { Location } from "../constants";
import * as d3 from "d3";

type Props = {
  locations: Location[];
  viewDate: Date;
  highlightedLocation: number | null;
  setHighlightedLocation: (v: number | null) => void;
};

const Timeline = ({
  locations,
  viewDate,
  highlightedLocation,
  setHighlightedLocation,
}: Props) => {
  const gY = useRef<SVGGElement | null>(null);
  const gDot = useRef<SVGGElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const startDT = new Date(viewDate.getTime());
  startDT.setHours(0);
  startDT.setMinutes(0);
  startDT.setSeconds(0);
  const endDT = new Date(viewDate.getTime());
  endDT.setHours(23);
  endDT.setMinutes(59);
  endDT.setSeconds(59);
  const y = d3.scaleTime().domain([startDT, endDT]).range([0, 500]);

  const [isZoomed, setIsZoomed] = useState(false);

  useEffect(() => {
    if (gY.current) {
      d3.select(gY.current).call(d3.axisLeft(y));
    }
  }, []);

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
    setIsZoomed(true);
    if (gDot.current) {
      d3.select(gDot.current)
        .attr("transform", dotTransform)
        .selectAll("circle")
        .attr("r", 8 / dotTransform.k)
        .attr("stroke-width", 2 / dotTransform.k);
    }
  };

  useEffect(() => {
    if (svgRef.current) {
      d3.select(svgRef.current).call(
        d3
          .zoom()
          .translateExtent([
            [0, 0],
            [0, 500],
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
        height="calc(100vh - 175px)"
        viewBox="-50 0 60 500"
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
              style={{cursor: 'pointer'}}
            />
          ))}
        </g>
      </svg>
    </div>
  );
};

export default Timeline;
