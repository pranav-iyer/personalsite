import * as pm from "./pixelmath.js";

let downOnHandle = false;
let downOnView = false;
let panStart = {
  mouseX: undefined,
  mouseY: undefined,
  x: undefined,
  y: undefined,
};
let LEFT_CANVAS = document.getElementById("left-canvas");
let RIGHT_CANVAS = document.getElementById("right-canvas");
let VIEW_CONTAINER = document.getElementById("view-container");
let PHOTO_DISPLAY = document.getElementById("two-photo-display");

let origWidth = 0;
let origHeight = 0;
let newWidth = 0;
let newHeight = 0;
let scaleFactor = 0.5;
let numColors = 10;

let currentPixelatedData = null;
let currentFilename = "";

let pointerCache = [];
let currentTouchDistance = -1;

let worker = new Worker("/static/pixelart/editor/pixelizer_worker.js", {
  type: "module",
});
worker.addEventListener("message", (event) => {
  if (event.data.status === "DONE") {
    currentPixelatedData = event.data.pixelatedData;
    putImageDataToCanvas(currentPixelatedData, RIGHT_CANVAS);

    stopLoading();
  } else if (event.data.status === "RUNNING") {
    let prog = document.getElementById("process-progress");
    prog.style["width"] = `${event.data.progress}%`;
  }
});

document
  .getElementById("two-photo-handle")
  .addEventListener("pointerdown", (event) => {
    // update pointer cache
    if (event.pointerType === "touch") {
      pointerCache.push({
        pointerId: event.pointerId,
        x: event.clientX,
        y: event.clientY,
      });

      if (pointerCache.length !== 2) {
        currentTouchDistance = -1;
      }
    }

    console.log("down on handle");
    downOnHandle = true;
    event.stopImmediatePropagation();
  });

VIEW_CONTAINER.addEventListener("pointerdown", (event) => {
  // update pointer cache
  if (event.pointerType === "touch") {
    pointerCache.push({
      pointerId: event.pointerId,
      x: event.clientX,
      y: event.clientY,
    });

    if (pointerCache.length !== 2) {
      currentTouchDistance = -1;
    }
  }

  console.log("down on view");
  downOnView = true;
  panStart = getPanInfo(event);
  console.log(panStart);
});

document.body.addEventListener("pointerup", (event) => {
  downOnHandle = false;
  downOnView = false;
  panStart = {
    mouseX: undefined,
    mouseY: undefined,
    x: undefined,
    y: undefined,
  };

  // remove event from pointer cache
  if (event.pointerType === "touch") {
    for (let i = 0; i < pointerCache.length; i++) {
      if (pointerCache[i].pointerId === event.pointerId) {
        pointerCache.splice(i, 1);
        break;
      }
    }

    if (pointerCache.length !== 2) {
      currentTouchDistance = -1;
    }
  }
});

function getPanInfo(event) {
  return {
    mouseX: event.clientX - VIEW_CONTAINER.offsetLeft,
    mouseY: event.clientY - VIEW_CONTAINER.offsetTop,
    x: getXProperty(),
    y: getYProperty(),
  };
}

PHOTO_DISPLAY.addEventListener("pointermove", (event) => {
  // update pointer cache
  if (event.pointerType === "touch") {
    for (let i = 0; i < pointerCache.length; i++) {
      if (pointerCache[i].pointerId === event.pointerId) {
        pointerCache[i].x = event.clientX;
        pointerCache[i].y = event.clientY;
        break;
      }
    }

    if (pointerCache.length === 2) {
      handleTouchZoom();
      return;
    }
  }

  if (downOnHandle) {
    if (event.clientX > 10 && event.clientX < VIEW_CONTAINER.clientWidth - 10) {
      PHOTO_DISPLAY.style.setProperty("--split-point", `${event.clientX}px`);
    }
  } else if (downOnView) {
    let currentPan = getPanInfo(event);
    setXProperty(currentPan.mouseX - panStart.mouseX + panStart.x);
    setYProperty(currentPan.mouseY - panStart.mouseY + panStart.y);
  }
});

function distanceBetween(p1, p2) {
  return Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2);
}

function getMidPoint(p1, p2) {
  return {
    x: 0.5 * (p1.x + p2.x),
    y: 0.5 * (p1.y + p2.y),
  };
}

function handleTouchZoom() {
  let curDist = distanceBetween(pointerCache[0], pointerCache[1]);
  let midPoint = getMidPoint(pointerCache[0], pointerCache[1]);

  if (currentTouchDistance > 0) {
    zoom(midPoint.x, midPoint.y, currentTouchDistance - curDist);
  }
  currentTouchDistance = curDist;
}

function getLeftCanvasCoords({ x, y }) {
  let clientRect = LEFT_CANVAS.getBoundingClientRect();
  return {
    x: ((x - clientRect.left) * LEFT_CANVAS.width) / clientRect.width,
    y: ((y - clientRect.top) * LEFT_CANVAS.height) / clientRect.height,
  };
}

PHOTO_DISPLAY.addEventListener("wheel", (event) => {
  event.preventDefault();
  event.stopImmediatePropagation();
  zoom(event.x, event.y, event.deltaY);
});

function zoom(x, y, deltaY) {
  let initScale = getScaleProperty();
  let newScale = pm.clamp(initScale - deltaY * 0.004, 0.1, 5);
  setScaleProperty(newScale);

  // translate so that it looks like we are zooming onto the mouse
  let { x: localX, y: localY } = getLeftCanvasCoords({
    x: x,
    y: y,
  });
  let oldX = getXProperty();
  let oldY = getYProperty();
  let newX = oldX - (newScale - initScale) * localX;
  let newY = oldY - (newScale - initScale) * localY;
  setXProperty(newX);
  setYProperty(newY);
}

function setScaleProperty(val) {
  PHOTO_DISPLAY.style.setProperty("--scale", val);
}

function getScaleProperty() {
  return parseFloat(PHOTO_DISPLAY.style.getPropertyValue("--scale"));
}

function setXProperty(val) {
  PHOTO_DISPLAY.style.setProperty("--x", `${val}px`);
}

function setYProperty(val) {
  PHOTO_DISPLAY.style.setProperty("--y", `${val}px`);
}

function getXProperty() {
  return parseFloat(PHOTO_DISPLAY.style.getPropertyValue("--x").slice(0, -2));
}

function getYProperty() {
  return parseFloat(PHOTO_DISPLAY.style.getPropertyValue("--y").slice(0, -2));
}

window.onresize = (event) => {
  if (
    parseInt(
      PHOTO_DISPLAY.style.getPropertyValue("--split-point").slice(0, -2)
    ) >
    VIEW_CONTAINER.clientWidth - 10
  ) {
    PHOTO_DISPLAY.style.setProperty(
      "--split-point",
      `${VIEW_CONTAINER.clientWidth - 10}px`
    );
  }
};

window.onload = () => {
  PHOTO_DISPLAY.style.setProperty(
    "--split-point",
    `${VIEW_CONTAINER.clientWidth / 2}px`
  );
  setXProperty(VIEW_CONTAINER.clientWidth / 2);
  setYProperty(VIEW_CONTAINER.clientHeight / 2);
  setScaleProperty(1);
  PHOTO_DISPLAY.style.setProperty("--right-scale", 1);
};

function setNewHeight(val) {
  newHeight = val;
  document.getElementById("new-height").innerText = val;
}

function setNewWidth(val) {
  newWidth = val;
  document.getElementById("new-width").innerText = val;
}

function setScaleFactor(val) {
  scaleFactor = val;
  document.getElementById("scale-factor").value = val;
}

function setOrigHeight(val) {
  origHeight = val;
  document.getElementById("orig-height").innerText = val;
}

function setOrigWidth(val) {
  origWidth = val;
  document.getElementById("orig-width").innerText = val;
}

function setNumColors(val) {
  numColors = val;
  document.getElementById("num-colors").innerText = val;
}

document.getElementById("photo-input").addEventListener("change", (event) => {
  const fileInput = document.getElementById("photo-input");
  let file = fileInput.files[0];
  if (file) {
    currentFilename = file.name.split(".").slice(0, -1).join(".");
    let reader = new FileReader();
    reader.addEventListener("load", (event) => {
      const im = new Image();
      im.src = event.target.result;
      im.onload = (event) => {
        startLoading();

        // store original width and height
        setOrigWidth(im.width);
        setOrigHeight(im.height);

        // default scale factor to get the result within 100x100px
        let largestDim = Math.max(im.width, im.height);
        setScaleFactor(Math.min(100 / largestDim, 0.5));

        PHOTO_DISPLAY.style.setProperty(
          "--split-point",
          `${VIEW_CONTAINER.clientWidth / 2}px`
        );

        translateToCenter(im);

        drawImageToCanvas(im, LEFT_CANVAS);

        const imageData = getCurrentImageData();
        removeAlpha(imageData);

        putImageDataToCanvas(imageData, LEFT_CANVAS);

        const [wNew, hNew] = pm.computeNewDims(
          imageData.width,
          imageData.height,
          scaleFactor
        );
        setNewWidth(wNew);
        setNewHeight(hNew);

        RIGHT_CANVAS.width = wNew;
        RIGHT_CANVAS.height = hNew;

        PHOTO_DISPLAY.style.setProperty("--right-scale", 1 / scaleFactor);

        clearCanvas(RIGHT_CANVAS);

        startProcessing(imageData);

        // currentPixelatedData = pixelate(imageData);

        // putImageDataToCanvas(currentPixelatedData, RIGHT_CANVAS);

        // stopLoading();
      };
    });
    reader.readAsDataURL(file);
  }
});

function clearCanvas(canvas) {
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#DDDDDD";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function startProcessing(imageData) {
  worker.postMessage({
    imData: imageData,
    scaleFactor: scaleFactor,
    numColors: numColors,
  });
}

function startLoading() {
  document.getElementById("controls-update-button").disabled = true;
  document.getElementById("pixart-download-button").disabled = true;
  document.getElementById("downloadOptionMenu").disabled = true;
  if (document.getElementById("save-library-trigger-button") !== null)
    document.getElementById("save-library-trigger-button").disabled = true;

  let prog = document.getElementById("process-progress");
  prog.style["width"] = `0%`;
}

function stopLoading() {
  document.getElementById("controls-update-button").disabled = false;
  document.getElementById("pixart-download-button").disabled = false;
  document.getElementById("downloadOptionMenu").disabled = false;
  if (document.getElementById("save-library-trigger-button") !== null)
    document.getElementById("save-library-trigger-button").disabled = false;

  let prog = document.getElementById("process-progress");
  prog.style["width"] = `100%`;
}

document
  .getElementById("controls-update-button")
  .addEventListener("click", (event) => {
    if (currentPixelatedData === null) return;
    startLoading();

    setScaleFactor(parseFloat(document.getElementById("scale-factor").value));
    setNumColors(parseInt(document.getElementById("num-colors").value));
    const imageData = getCurrentImageData();

    const [wNew, hNew] = pm.computeNewDims(
      imageData.width,
      imageData.height,
      scaleFactor
    );
    setNewWidth(wNew);
    setNewHeight(hNew);
    RIGHT_CANVAS.width = wNew;
    RIGHT_CANVAS.height = hNew;

    PHOTO_DISPLAY.style.setProperty("--right-scale", 1 / scaleFactor);

    clearCanvas(RIGHT_CANVAS);

    startProcessing(imageData);

    // currentPixelatedData = pixelate(imageData);

    // putImageDataToCanvas(currentPixelatedData, RIGHT_CANVAS);

    // stopLoading();
  });

function translateToCenter(im) {
  // change x and y to center image
  setXProperty(VIEW_CONTAINER.clientWidth / 2 - im.width / 2);
  setYProperty(VIEW_CONTAINER.clientHeight / 2 - im.height / 2);
  setScaleProperty(1);
}

function drawImageToCanvas(im, canvas) {
  canvas.width = im.width;
  canvas.height = im.height;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(im, 0, 0);
}

function putImageDataToCanvas(imageData, canvas) {
  canvas.width = imageData.width;
  canvas.height = imageData.height;
  const ctx = canvas.getContext("2d");
  ctx.putImageData(imageData, 0, 0);
}

function getCurrentImageData() {
  return LEFT_CANVAS.getContext("2d").getImageData(
    0,
    0,
    LEFT_CANVAS.width,
    LEFT_CANVAS.height
  );
}

function pixelate(imData) {
  return pm.clusterColors(pm.thumbnail(imData, scaleFactor), numColors);
}

function imageDataToPixart(imData) {
  let colors = [];
  let indices = new Array(imData.data.length / 4);
  for (let i = 0; i < imData.data.length; i += 4) {
    let foundMatch = false;
    for (let c = 0; c < colors.length; c++) {
      if (arrayEq(colors[c], imData.data.slice(i, i + 3))) {
        foundMatch = true;
        indices[i / 4] = c;
        break;
      }
    }
    if (!foundMatch) {
      indices[i / 4] = colors.length;
      colors.push(imData.data.slice(i, i + 3));
    }
  }

  colors = colors.map(pm.rgb2hex);

  let outStr = `dim ${imData.height} ${imData.width}\n`;
  // add colors
  outStr += "colors " + colors.join(" ") + "\n";
  for (let j = 0; j < imData.height; j++) {
    outStr +=
      indices
        .slice(imData.width * j, imData.width * (j + 1))
        .map((i) => i.toString().trim())
        .join(" ") + "\n";
  }

  return outStr;
}

function arrayEq(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;
  for (let i = 0; i < arr1.length; i++) {
    if (arr1[i] !== arr2[i]) return false;
  }
  return true;
}

function getInfoJsonContent(
  title,
  slug,
  pixart_fnam,
  thumb_fnam,
  gsthumb_fnam
) {
  return JSON.stringify({
    title: title,
    slug: slug,
    pixart_file: pixart_fnam,
    thumb_file: thumb_fnam,
    thumb_gs_file: gsthumb_fnam,
  });
}

document
  .getElementById("pixart-download-button")
  .addEventListener("click", (event) => {
    if (currentPixelatedData === null) return;
    let pixartContent = imageDataToPixart(currentPixelatedData);
    let blob = new Blob([pixartContent], {
      type: "text/plain",
    });
    saveAs(blob, currentFilename + ".pixart");
  });

document
  .getElementById("png-download-button")
  .addEventListener("click", (event) => {
    if (currentPixelatedData === null) return;
    RIGHT_CANVAS.toBlob((blob) => {
      saveAs(blob, currentFilename + "_pix.png");
    });
  });

document
  .getElementById("grayscale-download-button")
  .addEventListener("click", (event) => {
    if (currentPixelatedData === null) return;
    let gsData = pm.toGrayscale(currentPixelatedData);
    putImageDataToCanvas(gsData, RIGHT_CANVAS);
    RIGHT_CANVAS.toBlob((blob) => {
      saveAs(blob, currentFilename + "_pixgs.png");
      putImageDataToCanvas(currentPixelatedData, RIGHT_CANVAS);
    });
  });

document
  .getElementById("zip-download-button")
  .addEventListener("click", async (event) => {
    if (currentPixelatedData === null) return;
    let pixartFnam = currentFilename + ".pixart";
    let thumbFnam = currentFilename + "_pix.png";
    let gsThumbFnam = currentFilename + "_pixgs.png";
    let zip = new JSZip();
    zip.file(pixartFnam, imageDataToPixart(currentPixelatedData));
    zip.file(
      "info.json",
      getInfoJsonContent(
        currentFilename,
        slugify(currentFilename),
        pixartFnam,
        thumbFnam,
        gsThumbFnam
      )
    );

    RIGHT_CANVAS.toBlob((blob) => {
      zip.file(thumbFnam, blob);

      let gsData = pm.toGrayscale(currentPixelatedData);
      putImageDataToCanvas(gsData, RIGHT_CANVAS);
      RIGHT_CANVAS.toBlob((gsBlob) => {
        zip.file(gsThumbFnam, gsBlob);
        putImageDataToCanvas(currentPixelatedData, RIGHT_CANVAS);
        zip.generateAsync({ type: "blob" }).then((zipBlob) => {
          saveAs(zipBlob, currentFilename + ".zip");
        });
      });
    });
  });

document.getElementById("pixart-title").addEventListener("input", (event) => {
  let titleField = document.getElementById("pixart-title");
  let slugField = document.getElementById("pixart-slug");
  titleField.value = titleField.value.replace(/[^A-z ]/g, "");
  slugField.value = slugify(titleField.value);
});

let namingModal = document.getElementById("namingModal");
namingModal.addEventListener("show.bs.modal", (event) => {
  if (currentPixelatedData === null) event.preventDefault();
});

document
  .getElementById("save-library-button")
  .addEventListener("click", (event) => {
    if (currentPixelatedData === null) return;
    document.getElementById("error-text").innerText = "";
    let pixartFnam = currentFilename + ".pixart";
    let thumbFnam = currentFilename + "_pix.png";
    let gsThumbFnam = currentFilename + "_pixgs.png";
    let title = document.getElementById("pixart-title").value;
    let slug = document.getElementById("pixart-slug").value;
    let zip = new JSZip();
    zip.file(pixartFnam, imageDataToPixart(currentPixelatedData));
    zip.file(
      "info.json",
      getInfoJsonContent(title, slug, pixartFnam, thumbFnam, gsThumbFnam)
    );

    // make button a loading spinner
    let button = document.getElementById("save-library-button");
    button.disabled = true;
    button.querySelector(".spinner-border").classList.remove("d-none");

    RIGHT_CANVAS.toBlob((blob) => {
      zip.file(thumbFnam, blob);

      let gsData = pm.toGrayscale(currentPixelatedData);
      putImageDataToCanvas(gsData, RIGHT_CANVAS);
      RIGHT_CANVAS.toBlob((gsBlob) => {
        zip.file(gsThumbFnam, gsBlob);
        putImageDataToCanvas(currentPixelatedData, RIGHT_CANVAS);
        zip.generateAsync({ type: "blob" }).then((zipBlob) => {
          let csrftoken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
          ).value;
          let body = new FormData();
          body.append("zipfile", zipBlob, currentFilename + ".zip");

          fetch("/pixelart/zipdrop/", {
            method: "POST",
            headers: {
              "X-CSRFToken": csrftoken,
            },
            mode: "same-origin",
            body: body,
          })
            .then((res) => {
              if (res.ok) {
                // remove loading spinner
                let button = document.getElementById("save-library-button");
                button.disabled = false;
                button.querySelector(".spinner-border").classList.add("d-none");

                bootstrap.Modal.getInstance(
                  document.getElementById("namingModal")
                ).hide();
                document.getElementById("save-success-pixart-name").innerText =
                  title;
                bootstrap.Toast.getOrCreateInstance(
                  document.getElementById("success-toast")
                ).show();
              } else {
                const err = new Error("Zip Submission Error");
                err.res = res;
                throw err;
              }
            })
            .catch((err) => {
              return err.res.text().then((errText) => {
                document.getElementById("error-text").innerText = errText;

                // remove loading spinner
                let button = document.getElementById("save-library-button");
                button.disabled = false;
                button.querySelector(".spinner-border").classList.add("d-none");
              });
            });
        });
      });
    });
  });

function slugify(title) {
  return title.toLowerCase().replaceAll(" ", "-");
}

function removeAlpha(imData) {
  for (let i = 0; i < imData.data.length; i += 4) {
    imData.data[i + 3] = 255;
  }
}

document
  .getElementById("controls")
  .addEventListener("hidden.bs.collapse", (event) => {
    document.getElementById("collapse-icon-plus").style.display = "";
    document.getElementById("collapse-icon-minus").style.display = "none";
  });

document
  .getElementById("controls")
  .addEventListener("shown.bs.collapse", (event) => {
    document.getElementById("collapse-icon-plus").style.display = "none";
    document.getElementById("collapse-icon-minus").style.display = "";
  });
