import * as pm from "./pixelmath.js";

onmessage = function (e) {
  console.log("Worker: beginning image processing");
  let pixelatedData = pixelate(
    e.data.imData,
    e.data.scaleFactor,
    e.data.numColors,
    setProgress
  );
  postMessage({ status: "DONE", pixelatedData: pixelatedData });
};

function setProgress(curr, max) {
  postMessage({ status: "RUNNING", progress: Math.floor((curr * 100) / max) });
}

function pixelate(imData, scaleFactor, numColors, setProgress) {
  return pm.clusterColors(
    pm.thumbnail(imData, scaleFactor),
    numColors,
    setProgress
  );
}
