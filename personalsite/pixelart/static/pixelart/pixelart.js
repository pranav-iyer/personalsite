PIXI.Application.prototype.render = null; // Disable auto-rendering by removing the function
PIXI.sound.add("correct_click", "/static/pixelart/sounds/correct_click4.wav");
PIXI.sound.add("wrong_click", "/static/pixelart/sounds/wrong_click1.wav");

const sleep = (milliseconds) => {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
};

// constants (for now)
// const WIDTH = 900
// const HEIGHT = 600
// const MARGIN = 20
// const GRID_LEFT = MARGIN
// const GRID_TOP = MARGIN
const BACKGROUND_COLOR = 0xffffff;
const ACTIVE_COLOR = 0xaaaaaa;
// const FILL_DELAY = 200
// const FILL_RADIUS = 1
// const BUTTON_SPACE = 60
// const BUTTON_RADIUS = 25
// const SAFE_WIDTH = WIDTH - 2 * MARGIN - 2 * BUTTON_RADIUS + 40
// const SAFE_HEIGHT = HEIGHT - 2 * MARGIN
// const LIMITING_DIMENSION = Math.min(SAFE_WIDTH, SAFE_HEIGHT)
// const PANEL_NUM_COLORS = 7
// for reference
const ALL_STATUSES = ["inactive", "active", "wrong", "filled"];
const webGLVertexShader = `

precision mediump float;
attribute vec2 aVertexPosition;

uniform mat3 translationMatrix;
uniform mat3 projectionMatrix;

void main() {
    gl_Position = vec4((projectionMatrix * translationMatrix *
        vec3(aVertexPosition, 1.0)).xy, 0.0, 1.0);
}`;

function getWebGLFragShader(color) {
  const colorArray = PIXI.utils.hex2rgb(color);
  const colorString = `${colorArray[0]}, ${colorArray[1]}, ${colorArray[2]}, 1.0`;
  return `precision mediump float;

  void main() {
      gl_FragColor = vec4(${colorString});
  }

`;
}

function distanceBetween(p1, p2) {
  return Math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2);
}

function getMidPoint(p1, p2) {
  return {
    x: 0.5 * (p1.x + p2.x),
    y: 0.5 * (p1.y + p2.y),
  };
}

function mixRGB(currentColor, mixinColor, weight) {
  // mixes two colors specified as RGB arrays, with optional weight
  // to apply to second color
  // took from https://github.com/Qix-/color/blob/2df04512985147aa3a672453f38b18426fdf9d6c/index.js#L379
  // rather than importing entire color library
  const w1 = weight === undefined ? 0.5 : weight;
  const w2 = 1 - w1;

  return [
    w1 * mixinColor[0] + w2 * currentColor[0],
    w1 * mixinColor[1] + w2 * currentColor[1],
    w1 * mixinColor[2] + w2 * currentColor[2],
  ];
}

function getWrongColor(curColor) {
  return PIXI.utils.rgb2hex(
    mixRGB(PIXI.utils.hex2rgb(curColor), [0.625, 0.625, 0.625], 0.8)
  );
}

function compressStatuses(rawStatuses) {
  // takes in an array of status codes from 0 to 3, and returns a string with
  // the data compressed into a run-length encoding. The is is what will be
  // stored in the backend, and hopefully reduce some network load during gameplay.
  let compressedStatuses = "";
  let currentStatus = rawStatuses[0][0] === 3 ? 3 : 0;
  let numCurrent = 0;
  for (let i = 0; i < rawStatuses.length; i++) {
    for (let j = 0; j < rawStatuses[0].length; j++) {
      let newStatus = rawStatuses[i][j] === 3 ? 3 : 0;
      if (newStatus !== currentStatus) {
        compressedStatuses += `${currentStatus} ${numCurrent},`;
        currentStatus = newStatus;
        numCurrent = 1;
      } else {
        numCurrent += 1;
      }
    }
  }
  compressedStatuses += `${currentStatus} ${numCurrent},`;
  if (compressedStatuses.endsWith(",")) {
    compressedStatuses = compressedStatuses.slice(0, -1);
  }
  return compressedStatuses;
}

function decompressStatuses(statusString, numRows, numCols) {
  // takes in the run-length encoded status string, and expands it out
  // into a status array. Requires the row length parameter which should be calculated
  // from the pixelData.
  let statusArray = new Array(numRows);
  for (let i = 0; i < numRows; i++) {
    statusArray[i] = new Array(numCols);
  }
  let runLengthArray = statusString.split(",").map((row) => {
    return row.split(" ").map((value) => parseInt(value));
  });
  let i = 0;
  let j = 0;
  for (let run of runLengthArray) {
    for (let counter = 0; counter < run[1]; counter++) {
      statusArray[i][j] = run[0];
      j = j + 1;
      if (j >= numCols) {
        j = 0;
        i = i + 1;
      }
    }
  }

  return statusArray;
}

function isTouchDevice() {
  // from stackoverflow: https://stackoverflow.com/questions/4817029/whats-the-best-way-to-detect-a-touch-screen-device-using-javascript
  return (
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0
  );
}

function makeSquareGeom(coords) {
  return new PIXI.Geometry()
    .addAttribute("aVertexPosition", coords, 2)
    .addIndex([0, 1, 2, 0, 2, 3]);
}

class PixelArt {
  constructor(pixelData, pixelColors, statuses, config) {
    console.log(pixelColors);
    config = config ?? {};

    this.fillDelay = config.fillDelay ?? 200;
    this.fillRadius = config.fillRadius ?? 1;

    this.width = config.width ?? 500;
    this.height = config.height ?? 700;

    this.horizontalButtons = this.height > this.width;

    if (this.width < 400 || this.height < 400) {
      this.margin = config.margin ?? 7;
      this.buttonMargin = config.buttonMargin ?? 10;
      this.buttonRadius = config.buttonRadius ?? 20;
      this.highlightWidth = 10;
    } else {
      this.margin = config.margin ?? 15;
      this.buttonMargin = config.buttonMargin ?? 10;
      this.buttonRadius = config.buttonRadius ?? 25;
      this.highlightWidth = 13;
    }
    this.buttonSpace = 2 * this.buttonRadius + this.buttonMargin;

    if (this.horizontalButtons) {
      if (!isTouchDevice()) {
        this.panelNumColors =
          Math.floor(
            (this.width - 4 * this.margin - 2 * this.buttonRadius - 60) /
              this.buttonSpace
          ) + 1;
      } else {
        this.panelNumColors =
          Math.floor(
            (this.width - 4 * this.margin - 2 * this.buttonRadius) /
              this.buttonSpace
          ) + 1;
      }
    } else {
      if (!isTouchDevice()) {
        this.panelNumColors =
          Math.floor(
            (this.height - 4 * this.margin - 2 * this.buttonRadius - 25) /
              this.buttonSpace
          ) + 1;
      } else {
        this.panelNumColors =
          Math.floor(
            (this.height - 4 * this.margin - 2 * this.buttonRadius) /
              this.buttonSpace
          ) + 1;
      }
    }

    this.pixelData = pixelData;
    this.pixelColors = pixelColors;
    this.pixelColorShaders = this.pixelColors.map((c) => {
      return PIXI.Shader.from(webGLVertexShader, getWebGLFragShader(c));
    });
    this.pixelColorWrongShaders = this.pixelColors.map((c) => {
      return PIXI.Shader.from(
        webGLVertexShader,
        getWebGLFragShader(getWrongColor(c))
      );
    });
    this.activeColorShader = PIXI.Shader.from(
      webGLVertexShader,
      getWebGLFragShader(ACTIVE_COLOR)
    );

    if (this.horizontalButtons) {
      this.safe_width = this.width - 2 * this.margin;
      this.safe_height = this.height - 5 * this.margin - 2 * this.buttonRadius;
    } else {
      this.safe_width = this.width - 5 * this.margin - 2 * this.buttonRadius;
      this.safe_height = this.height - 2 * this.margin;
    }
    this.limitingDimensionIdx = +(
      this.safe_width / this.pixelData[0].length >=
      this.safe_height / this.pixelData.length
    );
    this.limitingDimension =
      this.limitingDimensionIdx === 0 ? this.safe_width : this.safe_height;

    this.gridSpace = 40;
    this.squareHitMargin = this.gridSpace / 10;

    this.squareGeom = makeSquareGeom([
      0,
      0,
      0,
      this.gridSpace,
      this.gridSpace,
      this.gridSpace,
      this.gridSpace,
      0,
    ]);

    this.fillSquareAnimGeoms = [
      makeSquareGeom([
        this.gridSpace / 2,
        0,
        this.gridSpace / 2,
        this.gridSpace,
        this.gridSpace / 2,
        this.gridSpace,
        this.gridSpace / 2,
        0,
      ]),
      makeSquareGeom([
        this.gridSpace / 2 - 5,
        0,
        this.gridSpace / 2 - 5,
        this.gridSpace,
        this.gridSpace / 2 + 5,
        this.gridSpace,
        this.gridSpace / 2 + 5,
        0,
      ]),
      makeSquareGeom([
        this.gridSpace / 2 - 10,
        0,
        this.gridSpace / 2 - 10,
        this.gridSpace,
        this.gridSpace / 2 + 10,
        this.gridSpace,
        this.gridSpace / 2 + 10,
        0,
      ]),
      makeSquareGeom([
        this.gridSpace / 2 - 15,
        0,
        this.gridSpace / 2 - 15,
        this.gridSpace,
        this.gridSpace / 2 + 15,
        this.gridSpace,
        this.gridSpace / 2 + 15,
        0,
      ]),
    ];

    PIXI.BitmapFont.from(
      "defaultFont",
      {
        fontFamily: "Arial",
        fontSize: this.gridSpace * 0.6,
        fill: 0x000000,
      },
      {
        chars: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "✓"],
      }
    );

    PIXI.BitmapFont.from(
      "defaultFontWhite",
      {
        fontFamily: "Arial",
        fontSize: this.gridSpace * 0.6,
        fill: 0xffffff,
      },
      {
        chars: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "✓"],
      }
    );

    this.fontColors = this.pixelColors.map((c) => {
      const rgb = PIXI.utils.hex2rgb(c).map((x) => x * 255);
      const useBlack = rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114 > 176;
      return useBlack ? 0x000000 : 0xffffff;
    });

    this.isDragging = false;
    this.dragStarted = false;
    this.fillMode = false;

    this.evCache = [];
    this.isZooming = false;
    this.touchDistance = -1;

    this.prevX = 0;
    this.prevY = 0;

    if (this.limitingDimensionIdx == 1) {
      this.minZoomLevel = Math.min(
        this.limitingDimension / (this.gridSpace * this.pixelData.length),
        1
      );
    } else {
      this.minZoomLevel = Math.min(
        this.limitingDimension / (this.gridSpace * this.pixelData[0].length),
        1
      );
    }
    if (statuses) {
      this.statuses = statuses;
    } else {
      this.statuses = this.pixelData.map((row) => row.map(() => 0));
    }

    this.app = new PIXI.Application({ width: this.width, height: this.height });
    this.playAreaContainer = new PIXI.Container();
    this.playAreaContainer.interactiveChildren = false;
    this.app.stage.addChild(this.playAreaContainer);
    this.gridContainer = new PIXI.Container();
    this.gridContainer.position.x = this.margin;
    this.gridContainer.position.y = this.margin;
    this.playAreaContainer.addChild(this.gridContainer);

    this.controlsContainer = new PIXI.Container();
    if (this.horizontalButtons) {
      this.controlsContainer.position.x = this.buttonRadius + 2 * this.margin;
      this.controlsContainer.position.y =
        this.height - this.buttonRadius - 2 * this.margin;
    } else {
      this.controlsContainer.position.x =
        this.width - this.buttonRadius - 2 * this.margin;
      this.controlsContainer.position.y = this.buttonRadius + 2 * this.margin;
    }
    this.app.stage.addChild(this.controlsContainer);

    // for logging on mobile where i can't see the console
    // this.log = new PIXI.Text("log", {
    //   fontFamily: "Arial",
    //   fontSize: 40,
    //   fill: 0x000000
    // })
    // this.log.position.x = 50
    // this.log.position.y = 50
    // this.app.stage.addChild(this.log)

    this.setupApp();
    this.setupGrid();
    this.setupControls();

    this.mousePosition = {
      x: 0,
      y: 0,
    };

    this.remainingPixels = this.pixelColors.map(() => 0);
    this.totalPixels = this.pixelColors.map(() => 0);
    this.pixelData.forEach((row, i) => {
      row.forEach((cell, j) => {
        if (cell === null) return;
        this.remainingPixels[cell] += 1;
        this.totalPixels[cell] += 1;
      });
    });

    for (let i = 0; i < this.statuses.length; i++) {
      for (let j = 0; j < this.statuses[i].length; j++) {
        if (this.statuses[i][j] === 3) {
          this.currentColor = this.pixelData[i][j];
          this.fillSquare(i, j, false);
          this.currentColor = -1;
        }
      }
    }

    this.setCurrentColor(-1);
    this.firstPanelColor = 0;
    this.updatePanelButtons();

    this.gridContainer.scale.x = this.minZoomLevel;
    this.gridContainer.scale.y = this.minZoomLevel;

    this.saveDirty = false;

    this.layoutDirty = true;
    this.app.ticker.add(() => {
      if (this.layoutDirty) {
        this.app.renderer.render(this.app.stage);
        this.layoutDirty = false;
      }
    });

    this.currentlyBouncing = {};
  }

  static async build(filename, status_string, config) {
    let text = "";
    await fetch(filename)
      .then((res) => res.text())
      .then((t) => (text = t));
    const lines = text.split("\n");
    const colors = lines[1].split(" ").slice(1).map(PIXI.utils.string2hex);
    const data = lines
      .slice(2)
      .filter((row) => row.trim() !== "")
      .map((row) =>
        row
          .trim()
          .split(" ")
          .map((x) => parseInt(x))
          .map((x) => (x < 0 ? null : x))
      );

    let statuses = false;
    if (status_string) {
      if (status_string.includes(",") || !status_string.includes("\n")) {
        statuses = decompressStatuses(
          status_string,
          data.length,
          data[0].length
        );
      } else {
        // parse statuses using legacy save format
        statuses = status_string
          .split("\n")
          .map((row) => row.split(" ").map((v) => parseInt(v)));

        console.log(
          "Existing save data is in legacy format. Will be upgraded to new save data format."
        );
      }
    }

    return new PixelArt(data, colors, statuses, config);
  }

  setupApp() {
    this.app.renderer.backgroundColor = BACKGROUND_COLOR;
    this.playAreaContainer.interactive = true;
    this.playAreaContainer.hitArea = new PIXI.Rectangle(
      0,
      0,
      this.safe_width,
      this.safe_height
    );
    this.playAreaContainer.on("pointerdown", (event) => {
      // zoom handling
      if (event.data.pointerType === "touch") {
        this.evCache.push({
          pointerId: event.data.pointerId,
          x: event.data.global.x,
          y: event.data.global.y,
        });
        if (this.evCache.length > 1) {
          this.isZooming = true;
        }
      }

      const pos = JSON.parse(JSON.stringify(event.data.global));
      this.mousePosition.x = pos.x;
      this.mousePosition.y = pos.y;
      this.prevX = pos.x;
      this.prevY = pos.y;
      this.isDragging = true;

      const currentMS = Date.now() % 1000;
      this.mousedownStarted = currentMS;

      const currentLocals = this.gridContainer.localTransform.applyInverse(pos);

      this.prevFilled = null;

      // check long press in similar location
      setTimeout(() => {
        if (
          this.isDragging &&
          !this.isZooming &&
          this.mousedownStarted === currentMS &&
          distanceBetween(pos, this.mousePosition) < this.fillRadius
        ) {
          this.fillMode = true;
          this.fillSquare(
            Math.floor(currentLocals.y / this.gridSpace),
            Math.floor(currentLocals.x / this.gridSpace)
          );
        }
      }, this.fillDelay);
    });
    this.playAreaContainer.on("pointermove", (event) => {
      // touch zoom handling
      if (event.data.pointerType === "touch") {
        for (let i = 0; i < this.evCache.length; i++) {
          if (this.evCache[i].pointerId === event.data.pointerId) {
            this.evCache[i].x = event.data.global.x;
            this.evCache[i].y = event.data.global.y;
            break;
          }
        }
        if (this.evCache.length === 2) {
          this.handleTouchZoom();
          return;
        }
      }

      if (!this.isDragging) return;

      this.mousePosition.x = event.data.global.x;
      this.mousePosition.y = event.data.global.y;

      if (this.fillMode && !this.isZooming) {
        const pos = JSON.parse(JSON.stringify(event.data.global));
        const currentLocals =
          this.gridContainer.localTransform.applyInverse(pos);
        const i = Math.floor(currentLocals.y / this.gridSpace);
        const j = Math.floor(currentLocals.x / this.gridSpace);
        if (
          i >= 0 &&
          i < this.pixelData.length &&
          j >= 0 &&
          j < this.pixelData[0].length
        ) {
          // fill any intermediate squares
          if (this.prevFilled) {
            let prevI = this.prevFilled.i;
            let prevJ = this.prevFilled.j;
            if (prevI - i === 2 && Math.abs(prevJ - j) <= 1) {
              // moved two to the left, and less than one vertically
              this.fillSquare(i + 1, j);
            } else if (prevI - i === -2 && Math.abs(prevJ - j) <= 1) {
              // moved two to the right, and less than one vertically
              this.fillSquare(i - 1, j);
            } else if (prevJ - j === 2 && Math.abs(prevI - i) <= 1) {
              // moved two squares down, and less than one horizontally
              this.fillSquare(i, j + 1);
            } else if (prevJ - j === -2 && Math.abs(prevI - i) <= 1) {
              // moved two squares up, and less than one horizontally
              this.fillSquare(i, j - 1);
            } else {
              // check for moving two squares diagonally
              if (prevI - i === 2 && prevJ - j === 2) {
                // 2 squares down and left
                this.fillSquare(i + 1, j + 1);
              } else if (prevI - i === -2 && prevJ - j === 2) {
                // 2 squares down and right
                this.fillSquare(i - 1, j + 1);
              } else if (prevI - i === -2 && prevJ - j === -2) {
                // 2 squares up and right
                this.fillSquare(i - 1, j - 1);
              } else if (prevI - i === 2 && prevJ - j === -2) {
                // 2 squares down and left
                this.fillSquare(i + 1, j - 1);
              }
            }
          }

          this.fillSquare(i, j);
          this.prevFilled = { i, j };
        }
      } else {
        var pos = event.data.global;
        var dx = pos.x - this.prevX;
        var dy = pos.y - this.prevY;
        if (this.dragStarted || Math.abs(dx) > 0.3 || Math.abs(dy) > 0.3) {
          this.dragStarted = true;
          if (
            (this.gridContainer.position.x >
              -(this.pixelData[0].length * this.gridSpace) *
                this.gridContainer.scale.x &&
              dx < 0) ||
            (this.gridContainer.position.x < this.safe_width && dx > 0)
          ) {
            this.gridContainer.position.x += dx;
          }
          if (
            (this.gridContainer.position.y >
              -(this.pixelData.length * this.gridSpace) *
                this.gridContainer.scale.y &&
              dy < 0) ||
            (this.gridContainer.position.y < this.safe_height && dy > 0)
          ) {
            this.gridContainer.position.y += dy;
          }
          this.layoutDirty = true;
        }
        this.prevX = pos.x;
        this.prevY = pos.y;
      }
    });
    this.playAreaContainer.on("pointerup", (event) => {
      // touch zoom handling
      if (event.data.pointerType === "touch") {
        this.remove_event(event);
        if (this.evCache.length < 2) {
          this.touchDistance = -1;
        }
      }

      // see if we need to fill the square we are on
      const pos = JSON.parse(JSON.stringify(event.data.global));
      const currentLocals = this.gridContainer.localTransform.applyInverse(pos);
      const i = Math.floor(currentLocals.y / this.gridSpace);
      const j = Math.floor(currentLocals.x / this.gridSpace);
      if (
        !this.dragStarted &&
        !this.isZooming &&
        this.numberTexts[i][j] !== null &&
        i >= 0 &&
        j >= 0 &&
        i < this.pixelData.length &&
        j < this.pixelData[0].length
      ) {
        this.fillSquare(i, j);
      }

      // get out of dragging mode
      this.isDragging = false;
      this.dragStarted = false;
      this.fillMode = false;
      if (event.data.pointerType === "touch" && this.evCache.length === 0) {
        this.isZooming = false;
      }
    });
    this.playAreaContainer.on("pointerupoutside", (event) => {
      this.isDragging = false;
      this.dragStarted = false;
      this.fillMode = false;

      // touch zoom handling
      if (event.data.pointerType === "touch") {
        this.remove_event(event);
        if (this.evCache.length < 2) {
          this.touchDistance = -1;
        }
        if (this.evCache.length === 0) {
          this.isZooming = false;
        }
      }
    });
    this.app.view.addEventListener("wheel", (event) => {
      event.preventDefault();
      this.handleZoom(this.mousePosition.x, this.mousePosition.y, event.deltaY);
    });
  }

  setupGrid() {
    // create container for each square
    this.squareGraphics = new Array(this.pixelData.length);
    for (let i = 0; i < this.pixelData.length; i++) {
      this.squareGraphics[i] = new Array(this.pixelData[i].length);
      for (let j = 0; j < this.pixelData[i].length; j++) {
        if (this.pixelData[i][j] === null) {
          this.squareGraphics[i][j] = null;
        } else {
          const grp = new PIXI.Container();
          this.gridContainer.addChild(grp);
          grp.position.x = this.gridSpace * j;
          grp.position.y = this.gridSpace * i;
          this.squareGraphics[i][j] = grp;
        }
      }
    }

    // add numbers in each square
    this.numberTextContainer = new PIXI.ParticleContainer(
      this.pixelData.length * this.pixelData[0].length
    );
    this.app.stage.addChild(this.numberTextContainer);
    this.gridContainer.addChild(this.numberTextContainer);

    this.numberTexts = new Array(this.pixelData.length);
    for (let i = 0; i < this.pixelData.length; i++) {
      this.numberTexts[i] = new Array(this.pixelData[i].length);
      for (let j = 0; j < this.pixelData[i].length; j++) {
        if (this.pixelData[i][j] === null) {
          this.numberTexts[i][j] = null;
        } else {
          let squareText = new PIXI.Sprite(
            PIXI.Loader.shared.resources[
              "/static/pixelart/numbers_spritesheet.json"
            ].textures[`num${this.pixelData[i][j]}.png`]
          );
          this.numberTextContainer.addChild(squareText);
          squareText.anchor.set(0.5);
          squareText.position.x =
            this.squareGraphics[i][j].position.x + this.gridSpace / 2;
          squareText.position.y =
            this.squareGraphics[i][j].position.y + this.gridSpace / 2;

          this.numberTexts[i][j] = squareText;
        }
      }
    }

    //add click listeners for each square and set hit boxes
    for (let i = 0; i < this.squareGraphics.length; i++) {
      for (let j = 0; j < this.squareGraphics[i].length; j++) {
        if (this.pixelData[i][j] !== null) {
          let grp = this.squareGraphics;
          grp.interactive = true;
          grp.hitArea = new PIXI.Rectangle(
            this.squareHitMargin,
            this.squareHitMargin,
            this.gridSpace - 2 * this.squareHitMargin,
            this.gridSpace - 2 * this.squareHitMargin
          );
        }
      }
    }
  }

  setupControls() {
    if (this.horizontalButtons) {
      let panelWidth =
        2 * this.buttonRadius +
        (this.panelNumColors - 1) * this.buttonSpace +
        2 * this.margin;
      if (!isTouchDevice()) panelWidth += 60;
      const buttonPanel = new PIXI.Graphics();
      this.controlsContainer.addChild(buttonPanel);
      buttonPanel.lineStyle(2, 0x000000);
      buttonPanel.beginFill(BACKGROUND_COLOR);
      buttonPanel.drawRoundedRect(
        -this.buttonRadius - this.margin,
        -this.buttonRadius - this.margin,
        panelWidth,
        2 * this.buttonRadius + 2 * this.margin
      );
    } else {
      let panelHeight =
        2 * this.buttonRadius +
        (this.panelNumColors - 1) * this.buttonSpace +
        2 * this.margin;
      if (!isTouchDevice()) panelHeight += 25;
      const buttonPanel = new PIXI.Graphics();
      this.controlsContainer.addChild(buttonPanel);
      buttonPanel.lineStyle(2, 0x000000);
      buttonPanel.beginFill(BACKGROUND_COLOR);
      buttonPanel.drawRoundedRect(
        -this.buttonRadius - this.margin,
        -this.buttonRadius - this.margin,
        2 * this.buttonRadius + 2 * this.margin,
        panelHeight
      );
    }

    if (!isTouchDevice()) {
      this.nextColorPageButton = new PIXI.Graphics();
      this.controlsContainer.addChild(this.nextColorPageButton);
      this.nextColorPageButton.interactive = true;
      this.nextColorPageButton.on("click", () => {
        if (
          this.firstPanelColor + this.panelNumColors <
          this.pixelColors.length
        ) {
          this.firstPanelColor += this.panelNumColors;
          this.updatePanelButtons();
        }
      });

      this.prevColorPageButton = new PIXI.Graphics();
      this.controlsContainer.addChild(this.prevColorPageButton);
      this.prevColorPageButton.interactive = true;
      this.prevColorPageButton.on("click", () => {
        if (this.firstPanelColor >= this.panelNumColors) {
          this.firstPanelColor -= this.panelNumColors;
          this.updatePanelButtons();
        }
      });
    } else {
      // add swipe listener for button changing
      this.panelTouchPositionX = null;
      this.panelTouchPositionY = null;
      this.panelTouchStarted = null;
      this.controlsContainer.on("touchstart", (event) => {
        this.panelTouchPositionX = event.data.global.x;
        this.panelTouchPositionY = event.data.global.y;
        this.panelTouchStarted = Date.now();
      });
      this.controlsContainer.on("touchend", (event) => {
        if (this.panelTouchStarted === null) return;
        if (this.horizontalButtons) {
          if (Math.abs(this.panelTouchPositionY - event.data.global.y) > 30)
            return;
        } else {
          if (Math.abs(this.panelTouchPositionX - event.data.global.x) > 30)
            return;
        }
        if (Date.now() - this.panelTouchStarted > 250) return;
        let parallelDist;
        if (this.horizontalButtons) {
          parallelDist = event.data.global.x - this.panelTouchPositionX;
        } else {
          parallelDist = event.data.global.y - this.panelTouchPositionY;
        }
        if (parallelDist > 60) {
          if (this.firstPanelColor >= this.panelNumColors) {
            this.firstPanelColor -= this.panelNumColors;
            this.updatePanelButtons();
          }
        } else if (parallelDist < -60) {
          if (
            this.firstPanelColor + this.panelNumColors <
            this.pixelColors.length
          ) {
            this.firstPanelColor += this.panelNumColors;
            this.updatePanelButtons();
          }
        }
      });
      this.controlsContainer.on("touchcancel", (event) => {
        this.panelTouchPositionX = null;
        this.panelTouchPositionY = null;
        this.panelTouchStarted = null;
      });
      this.controlsContainer.interactive = true;
    }

    this.colorHighlightRing = new PIXI.Graphics();
    this.controlsContainer.addChild(this.colorHighlightRing);

    this.panelButtonContainer = new PIXI.Container();
    this.controlsContainer.addChild(this.panelButtonContainer);

    this.updatePanelButtons();
  }

  updatePanelButtons() {
    let oldChildren = this.panelButtonContainer.removeChildren();
    for (let i = 0; i < oldChildren.length; i++) {
      oldChildren[i].destroy();
    }
    this.pixelColors
      .slice(this.firstPanelColor, this.firstPanelColor + this.panelNumColors)
      .forEach((color, i) => {
        const button = new PIXI.Graphics();
        button.interactive = true;
        this.panelButtonContainer.addChild(button);
        button.lineStyle(2, 0x000000);
        button.beginFill(color);
        if (this.horizontalButtons) {
          button.drawCircle(this.buttonSpace * i, 0, this.buttonRadius);
        } else {
          button.drawCircle(0, this.buttonSpace * i, this.buttonRadius);
        }

        const thisColorIdx = i + this.firstPanelColor;
        const buttonLabel = new PIXI.BitmapText(
          this.remainingPixels[thisColorIdx] > 0 ? `${thisColorIdx}` : "✓",
          {
            fontName:
              this.fontColors[thisColorIdx] === 0x000000
                ? "defaultFont"
                : "defaultFontWhite",
          }
        );
        buttonLabel.anchor.set(0.5);
        if (this.horizontalButtons) {
          buttonLabel.position.x = this.buttonSpace * i;
        } else {
          buttonLabel.position.y = this.buttonSpace * i;
        }
        button.addChild(buttonLabel);

        button.on("pointertap", () => {
          this.setCurrentColor(thisColorIdx);
          this.updateHighlightRing();
        });
      });

    this.updateHighlightRing();

    if (!isTouchDevice()) {
      let nextTriangle, prevTriangle;
      if (this.horizontalButtons) {
        const rightOfRightCircle =
          (this.panelNumColors - 1) * this.buttonSpace + this.buttonRadius + 35;
        nextTriangle = [
          rightOfRightCircle + 5,
          -10,
          rightOfRightCircle + 5,
          10,
          rightOfRightCircle + this.buttonRadius,
          0,
        ];
        prevTriangle = [
          rightOfRightCircle - 5,
          -10,
          rightOfRightCircle - 5,
          10,
          rightOfRightCircle - this.buttonRadius,
          0,
        ];
      } else {
        const bottomOfBottomCircle =
          (this.panelNumColors - 1) * this.buttonSpace + this.buttonRadius;
        nextTriangle = [
          5,
          bottomOfBottomCircle + 10,
          5,
          bottomOfBottomCircle + 30,
          this.buttonRadius,
          bottomOfBottomCircle + 20,
        ];
        prevTriangle = [
          -5,
          bottomOfBottomCircle + 10,
          -5,
          bottomOfBottomCircle + 30,
          -this.buttonRadius,
          bottomOfBottomCircle + 20,
        ];
      }

      // next page button
      this.nextColorPageButton.clear();
      if (
        this.firstPanelColor + this.panelNumColors >=
        this.pixelColors.length
      ) {
        this.nextColorPageButton.lineStyle(2, 0xcccccc);
        this.nextColorPageButton.beginFill(0xcccccc);
        this.nextColorPageButton.drawPolygon(nextTriangle);
      } else {
        this.nextColorPageButton.lineStyle(2, 0x000000);
        this.nextColorPageButton.beginFill(0x000000);
        this.nextColorPageButton.drawPolygon(nextTriangle);
      }

      // prev page button
      this.prevColorPageButton.clear();
      if (this.firstPanelColor < this.panelNumColors) {
        this.prevColorPageButton.lineStyle(2, 0xcccccc);
        this.prevColorPageButton.beginFill(0xcccccc);
        this.prevColorPageButton.drawPolygon(prevTriangle);
      } else {
        this.prevColorPageButton.lineStyle(2, 0x000000);
        this.prevColorPageButton.beginFill(0x000000);
        this.prevColorPageButton.drawPolygon(prevTriangle);
      }
    }
  }

  updateHighlightRing() {
    this.layoutDirty = true;
    this.colorHighlightRing.clear();
    if (
      this.currentColor >= this.firstPanelColor &&
      this.currentColor < this.firstPanelColor + this.panelNumColors &&
      this.currentColor >= 0 &&
      this.remainingPixels[this.currentColor] > 0
    ) {
      const frac =
        1 -
        this.remainingPixels[this.currentColor] /
          this.totalPixels[this.currentColor];
      this.colorHighlightRing.lineStyle(this.highlightWidth, 0xaaaaaa);
      this.colorHighlightRing.drawCircle(0, 0, this.buttonRadius);
      this.colorHighlightRing.lineStyle(this.highlightWidth, 0x000000);
      this.colorHighlightRing.arc(
        0,
        0,
        this.buttonRadius,
        1.5 * Math.PI,
        (1.5 + frac * 2) * Math.PI
      );
      if (this.horizontalButtons) {
        this.colorHighlightRing.position.x =
          this.buttonSpace * (this.currentColor - this.firstPanelColor);
      } else {
        this.colorHighlightRing.position.y =
          this.buttonSpace * (this.currentColor - this.firstPanelColor);
      }
    }
  }

  setCurrentColor(i) {
    if (this.remainingPixels[i] === 0) {
      if (this.currentColor === i) {
        this.currentColor = -1;
      } else {
        return;
      }
    }
    this.currentColor = i;
    this.updateHighlightRing();

    // color all of the corresponding squares grey, and non-corresponding ones white
    this.pixelData.forEach((row, i) => {
      row.forEach((cell, j) => {
        if (cell === this.currentColor) {
          this.setSquareActive(i, j);
        } else {
          this.setSquareInactive(i, j);
        }
      });
    });
  }

  remove_event(ev) {
    for (let i = 0; i < this.evCache.length; i++) {
      if (this.evCache[i].pointerId === ev.data.pointerId) {
        this.evCache.splice(i, 1);
        break;
      }
    }
  }

  handleTouchZoom() {
    let curDist = distanceBetween(this.evCache[0], this.evCache[1]);
    let midPoint = getMidPoint(this.evCache[0], this.evCache[1]);
    // this.log.text = curDist
    if (this.touchDistance > 0) {
      this.handleZoom(midPoint.x, midPoint.y, this.touchDistance - curDist);
    }
    this.touchDistance = curDist;
  }

  handleZoom(x, y, deltaY) {
    if (this.gridContainer.scale.x < this.minZoomLevel && deltaY > 0) return;
    if (this.gridContainer.scale.x > 3 && deltaY < 0) return;

    this.layoutDirty = true;

    // scale up by delta factor
    const zoomFactor =
      deltaY > 0 ? Math.min(deltaY, 13) : Math.max(deltaY, -13);

    const beforeGlobal = { x, y };
    const beforeLocal =
      this.gridContainer.localTransform.applyInverse(beforeGlobal);

    const oldScaleX = this.gridContainer.scale.x;
    const newScaleX = oldScaleX * (1 - 0.005 * zoomFactor);
    const oldScaleY = this.gridContainer.scale.y;
    const newScaleY = oldScaleY * (1 - 0.005 * zoomFactor);

    this.gridContainer.scale.x = newScaleX;
    this.gridContainer.scale.y = newScaleY;

    const dx = -beforeLocal.x * (newScaleX - oldScaleX);
    const dy = -beforeLocal.y * (newScaleY - oldScaleY);

    this.gridContainer.position.x += dx;
    this.gridContainer.position.y += dy;
  }

  fillSquare(i, j, animate = true) {
    this.layoutDirty = true;
    if (this.currentColor < 0) return;
    if (this.pixelData[i][j] === null) return;
    if (this.numberTexts[i][j] === null) return;
    const grp = this.squareGraphics[i][j];

    grp.removeChildren();
    if (this.currentColor === this.pixelData[i][j]) {
      this.numberTexts[i][j].destroy();
      this.numberTexts[i][j] = null;

      if (animate) {
        PIXI.sound.play("correct_click");

        setTimeout(async () => {
          let shader = this.pixelColorShaders[this.pixelData[i][j]];
          for (let i = 0; i < this.fillSquareAnimGeoms.length; i++) {
            grp.removeChildren();
            let filledSquare = new PIXI.Mesh(
              this.fillSquareAnimGeoms[i],
              shader
            );
            grp.addChild(filledSquare);
            this.layoutDirty = true;
            await sleep(25);
          }

          grp.removeChildren();
          let filledSquare = new PIXI.Mesh(this.squareGeom, shader);
          grp.addChild(filledSquare);

          this.statuses[i][j] = 3;
          this.saveDirty = true;
          this.remainingPixels[this.pixelData[i][j]] -= 1;
          this.updatePanelButtons();
          if (!this.remainingPixels.some((n) => n > 0)) {
            this.complete();
          }
        }, 0);
      } else {
        grp.removeChildren();
        let shader = this.pixelColorShaders[this.pixelData[i][j]];
        let filledSquare = new PIXI.Mesh(this.squareGeom, shader);
        grp.addChild(filledSquare);

        this.statuses[i][j] = 3;
        this.saveDirty = true;
        this.remainingPixels[this.pixelData[i][j]] -= 1;
        this.updatePanelButtons();
        if (!this.remainingPixels.some((n) => n > 0)) {
          this.complete();
        }
      }
    } else {
      let shader = this.pixelColorWrongShaders[this.currentColor];
      let filledSquare = new PIXI.Mesh(this.squareGeom, shader);
      grp.addChild(filledSquare);

      this.statuses[i][j] = 2;

      if (animate && !this.currentlyBouncing[`${i},${j}`]) {
        let startX = j * this.gridSpace;
        let startY = i * this.gridSpace;

        PIXI.sound.play("wrong_click");

        this.currentlyBouncing[`${i},${j}`] = true;

        setTimeout(async () => {
          for (let new_scale of [1, 0.8, 0.8, 0.9, 0.95, 1]) {
            console.log(new_scale);
            grp.scale.x = new_scale;
            grp.scale.y = new_scale;
            grp.position.x = startX + (this.gridSpace * (1 - new_scale)) / 2;
            grp.position.y = startY + (this.gridSpace * (1 - new_scale)) / 2;
            this.layoutDirty = true;
            await sleep(30);
          }
          this.currentlyBouncing[`${i},${j}`] = false;
        }, 0);
      }
    }
  }

  setSquareActive(i, j) {
    if (this.statuses[i][j] !== 0 || this.pixelData[i][j] === null) {
      return;
    } else {
      const grp = this.squareGraphics[i][j];

      grp.removeChildren();
      let shader = this.activeColorShader;
      let filledSquare = new PIXI.Mesh(this.squareGeom, shader);
      grp.addChild(filledSquare);

      this.statuses[i][j] = 1;
    }
  }

  setSquareInactive(i, j) {
    if (this.statuses[i][j] !== 1 || this.pixelData[i][j] == null) {
      return;
    } else {
      const grp = this.squareGraphics[i][j];
      grp.removeChildren();
      this.statuses[i][j] = 0;
    }
  }

  complete() {
    const completionText = new PIXI.Text("✓", {
      fontFamily: "Arial",
      fontSize: 200,
      fill: 0xffffff,
    });
    completionText.anchor.set(0.5);
    completionText.position.x = this.gridSpace * (this.pixelData[0].length / 2);
    completionText.position.y = this.gridSpace * (this.pixelData.length / 2);
    this.gridContainer.addChild(completionText);
    this.layoutDirty = true;

    // zoom all the way out to show completed image
    let zoomOut = () => {
      if (
        this.gridContainer.scale.x <= this.minZoomLevel &&
        this.gridContainer.position.x === this.margin &&
        this.gridContainer.position.y === this.margin
      )
        return;

      if (this.gridContainer.scale.x > this.minZoomLevel) {
        this.gridContainer.scale.x *= 0.95;
        this.gridContainer.scale.y *= 0.95;
      }

      if (
        this.gridContainer.position.x <= 2 * this.margin &&
        this.gridContainer.position.x >= 0
      ) {
        this.gridContainer.position.x = this.margin;
      } else {
        if (this.gridContainer.position.x < this.margin) {
          this.gridContainer.position.x += 10;
        } else {
          this.gridContainer.position.x -= 10;
        }
      }

      if (
        this.gridContainer.position.y <= 2 * this.margin &&
        this.gridContainer.position.y >= 0
      ) {
        this.gridContainer.position.y = this.margin;
      } else {
        if (this.gridContainer.position.y < this.margin) {
          this.gridContainer.position.y += 5;
        } else {
          this.gridContainer.position.y -= 5;
        }
      }

      console.log(
        this.gridContainer.position.x,
        this.gridContainer.position.y,
        this.gridContainer.scale.x
      );

      this.app.renderer.render(this.app.stage);
      requestAnimationFrame(zoomOut);
    };
    requestAnimationFrame(zoomOut);
  }

  getSaveData() {
    let data = new FormData();
    data.append(
      "progress",
      1 -
        this.remainingPixels.reduce((prev, cur) => prev + cur) /
          this.totalPixels.reduce((prev, cur) => prev + cur)
    );
    // data.append("statuses", this.statuses.map( (row) => row.join(" ") ).join("\n") ); //creates legacy saves
    data.append("statuses", compressStatuses(this.statuses)); //creates new save format
    this.saveDirty = false;
    return data;
  }
}

export default PixelArt;
