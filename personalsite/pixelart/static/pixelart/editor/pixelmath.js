export function hex2rgb(hex) {
  return [
    convertToNum(hex.slice(1, 3)),
    convertToNum(hex.slice(3, 5)),
    convertToNum(hex.slice(5, 7)),
  ];
}

export function rgb2hex(rgb) {
  let result = "#";
  for (let i = 0; i < 3; i++) {
    result += convertToHex(rgb[i]);
  }
  return result;
}

function convertToNum(hexStr) {
  return parseInt(hexStr, 16);
}

function convertToHex(num) {
  let s = Number(num).toString(16);
  if (s.length === 1) s = "0" + s;
  return s;
}

function randInt(min, max) {
  return Math.floor((max - min) * Math.random()) + min;
}

function imageDataToColors(imData) {
  let result = new Array(imData.data.length / 4);
  for (let i = 0; i < result.length; i++) {
    result[i] = imData.data.slice(4 * i, 4 * i + 4);
  }
  return result;
}

function computeVariance(data, clusters, indices) {
  let varn = 0;
  for (let i = 0; i < indices.length; i++) {
    let clusterColor = clusters[indices[i]];
    let dist = distance(data[i], clusterColor);
    varn += dist * dist;
  }
  console.log(varn);
  return varn;
}

function kMeans(data, num_clusters, num_iters, num_trials, setProgress) {
  let num_points = data.length;

  let clusterDists = new Array(num_clusters);
  let closestClusters = new Array(num_clusters);
  for (let i = 0; i < num_clusters; i++) {
    clusterDists[i] = new Array(num_clusters).fill(0);
    closestClusters[i] = new Array(num_clusters).fill(0);
  }

  let bestIndices = null;
  let bestClusters = null;
  let bestVariance = Infinity;

  let theseIndices = new Uint32Array(data.length);
  let theseClusters = new Array(num_clusters);

  for (let trial = 0; trial < num_trials; trial++) {
    // initialize clusters (to random data values)
    for (let c = 0; c < num_clusters; c++) {
      let idx = randInt(0, data.length);
      theseClusters[c] = data[idx];
    }

    for (let iter = 0; iter < num_iters; iter++) {
      // compute pairwise distances between clusters
      for (let i = 0; i < num_clusters; i++) {
        for (let j = i + 1; j < num_clusters; j++) {
          const thisDist = distance(theseClusters[i], theseClusters[j]);
          clusterDists[i][j] = thisDist;
          clusterDists[j][i] = thisDist;
        }
      }

      // sort clusters by distance, store in closestClusters matrix
      for (let i = 0; i < num_clusters; i++) {
        closestClusters[i] = clusterDists[i]
          .map((v, i) => [i, v])
          .sort((a, b) => a[1] - b[1])
          .map((x) => x[0]);
      }

      // assignment step
      for (let i = 0; i < num_points; i++) {
        let prevIndex = theseIndices[i];
        let prevDist,
          minDist = distance(theseClusters[prevIndex], data[i]);
        for (let c = 1; c < num_clusters; c++) {
          let t = closestClusters[prevIndex][c];
          if (clusterDists[prevIndex][t] >= 4 * prevDist) {
            // by triangle inequality, this cluster is eliminated
            break;
          }
          let currDist = distance(theseClusters[t], data[i]);
          if (currDist < minDist) {
            minDist = currDist;
            theseIndices[i] = t;
          }
        }
      }

      // update step
      for (let c = 0; c < num_clusters; c++) {
        // get mean of all points in cluster
        let center = new Array(data[0].length).fill(0);
        let num_in_cluster = 0;

        for (let i = 0; i < num_points; i++) {
          if (theseIndices[i] === c) {
            for (let k = 0; k < data[0].length; k++) {
              center[k] += data[i][k];
            }
            num_in_cluster += 1;
          }
        }

        if (num_in_cluster !== 0) {
          theseClusters[c] = center.map((x) => x / num_in_cluster);
        } else {
          let idx = randInt(0, data.length);
          theseClusters[c] = data[idx];
        }
      }
      if (iter % 5 === 0)
        setProgress(trial * num_iters + iter + 1, num_trials * num_iters);
    }

    let thisVariance = computeVariance(data, theseClusters, theseIndices);
    if (thisVariance < bestVariance) {
      bestVariance = thisVariance;
      bestClusters = theseClusters;
      bestIndices = theseIndices;
    }
  }
  console.log("best var", bestVariance);

  return {
    clusters: bestClusters,
    indices: bestIndices,
  };
}

function argmin(arr) {
  let minSoFar = arr[0];
  let minIndex = 0;
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] < minSoFar) {
      minSoFar = arr[i];
      minIndex = i;
    }
  }
  return minIndex;
}

function distance(p1, p2) {
  let res = 0;
  for (let i = 0; i < p1.length; i++) {
    res += (p2[i] - p1[i]) * (p2[i] - p1[i]);
  }
  return res;
}

function average(data) {
  if (!isIterable(data[0])) {
    let result = 0;
    for (let i = 0; i < data.length; i++) {
      result += data[i];
    }
    return result / data.length;
  } else {
    let result = new Array(data[0].length).fill(0);
    for (let i = 0; i < data.length; i++) {
      for (let j = 0; j < data[i].length; j++) {
        result[j] += data[i][j];
      }
    }
    return result.map((x) => x / data.length);
  }
}

function isIterable(obj) {
  // copied from stackoverflow: https://stackoverflow.com/questions/30061205/check-if-object-is-collection-iterable
  if (obj == null) {
    return false;
  }
  return typeof obj[Symbol.iterator] === "function";
}

export function computeNewDims(w, h, s) {
  return [Math.floor(w * s), Math.floor(h * s)];
}

export function thumbnail(image, scale) {
  const old_width = image.width;
  const old_height = image.height;
  const [new_width, new_height] = computeNewDims(
    image.width,
    image.height,
    scale
  );

  console.log(new_width, new_height);

  // how to down size?
  let strideX = old_width / new_width;
  let strideY = old_height / new_height;

  let new_image = new ImageData(new_width, new_height);
  for (let j = 0; j < new_height; j++) {
    for (let i = 0; i < new_width; i++) {
      let avgs = [0, 0, 0, 0];
      let count = 0;
      // compute average of all pixel values in area in original image
      for (
        let jsrc = Math.floor(j * strideY);
        jsrc < Math.floor((j + 1) * strideY);
        jsrc++
      ) {
        for (
          let isrc = Math.floor(i * strideX);
          isrc < Math.floor((i + 1) * strideX);
          isrc++
        ) {
          let src_cell_start = 4 * (old_width * jsrc + isrc);
          for (let k = 0; k < avgs.length; k++) {
            avgs[k] += image.data[src_cell_start + k];
          }
          count += 1;
        }
      }
      for (let k = 0; k < avgs.length; k++) {
        avgs[k] = avgs[k] / count;
      }
      // console.log(avgs);

      let cell_start = 4 * (new_width * j + i);
      new_image.data[cell_start] = avgs[0];
      new_image.data[cell_start + 1] = avgs[1];
      new_image.data[cell_start + 2] = avgs[2];
      new_image.data[cell_start + 3] = avgs[3];
    }
  }

  console.log(new_image);

  return new_image;
}

export function clamp(val, lo, hi) {
  if (val <= lo) {
    return lo;
  } else if (val <= hi) {
    return val;
  } else {
    return hi;
  }
}

export function clusterColors(imData, numColors, setProgress) {
  let colorArray = imageDataToColors(imData);
  // convert colors to yuv for clustering
  for (let i = 0; i < colorArray.length; i++) {
    colorArray[i] = rgb2yuv(colorArray[i]);
  }

  let kMeansResult = kMeans(colorArray, numColors, 10, 20, setProgress);

  // convert result back to rgb for drawing
  for (let i = 0; i < kMeansResult.clusters.length; i++) {
    kMeansResult.clusters[i] = yuv2rgb(kMeansResult.clusters[i]);
  }

  let newImage = new ImageData(imData.width, imData.height);
  for (let i = 0; i < imData.data.length; i += 4) {
    const col = kMeansResult.clusters[kMeansResult.indices[i / 4]];
    for (let k = 0; k < 4; k++) {
      newImage.data[i + k] = col[k];
    }
  }
  return newImage;
}

function rgb2yuv(rgb) {
  return [
    0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2],
    -0.147 * rgb[0] - 0.289 * rgb[1] + 0.436 * rgb[2],
    0.615 * rgb[0] - 0.515 * rgb[1] - 0.1 * rgb[2],
    rgb[3],
  ];
}

function yuv2rgb(yuv) {
  return [
    yuv[0] + 1.14 * yuv[2],
    yuv[0] - 0.395 * yuv[1] - 0.581 * yuv[2],
    yuv[0] + 2.032 * yuv[1],
    yuv[3],
  ];
}

export function toGrayscale(imData) {
  let newData = new ImageData(imData.width, imData.height);
  for (let i = 0; i < imData.data.length; i += 4) {
    const y =
      (0.299 * imData.data[i] +
        0.587 * imData.data[i + 1] +
        0.114 * imData.data[i + 2]) /
        2 +
      127;
    newData.data[i] = y;
    newData.data[i + 1] = y;
    newData.data[i + 2] = y;
    newData.data[i + 3] = 255;
  }
  return newData;
}
