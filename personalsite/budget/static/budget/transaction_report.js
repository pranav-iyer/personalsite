function formatDate(d) {
  return `${d.slice(5, 7)}/${d.slice(8, 10)}/${d.slice(0, 4)}`;
}

function filterInPlace(data, filters) {
  let filter_colnames = Object.keys(filters);
  // strip off some common prefixes that shouldn't be searchable
  let prefixes = ["digital card purchase", "debit card purchase"];

  for (let row of data) {
    let should_show = true;
    for (let col of filter_colnames) {
      if (filters[col] === null) {
        should_show = should_show && true;
      } else {
        if (filters[col].type === "exact") {
          should_show = should_show && row[col] === filters[col].fil;
        } else if (filters[col].type === "range") {
          let num = parseFloat(row[col]);
          should_show =
            should_show &&
            num >= filters[col].fil[0] &&
            num <= filters[col].fil[1];
        } else if (filters[col].type === "daterange") {
          should_show =
            should_show &&
            row[col] >= filters[col].fil[0] &&
            row[col] <= filters[col].fil[1];
        } else {
          let currVal = row[col].toLowerCase();
          for (let prefix of prefixes) {
            if (currVal.startsWith(prefix)) {
              currVal = currVal.slice(prefix.length);
            }
          }
          should_show =
            should_show && currVal.includes(filters[col].fil.toLowerCase());
        }
      }
    }
    row.hidden = !should_show;
  }
}

function sortInPlace(data, col, dtype, order) {
  if (dtype === "number" || dtype === "money") {
    data.sort((a, b) => order * (a[col] - b[col]));
  } else if (dtype === "string") {
    data.sort((a, b) => {
      let newA = a[col].toString().toUpperCase();
      let newB = b[col].toString().toUpperCase();
      if (newA < newB) {
        return -1 * order;
      } else if (newA > newB) {
        return 1 * order;
      } else {
        return 0;
      }
    });
  } else if (dtype === "date") {
    data.sort((a, b) => {
      if (a[col] < b[col]) {
        return -1 * order;
      } else if (b[col] < a[col]) {
        return 1 * order;
      } else {
        return 0;
      }
    });
  } else {
    throw RuntimeError("dtype must be number, money, string or date.");
  }
}

function fillTbody(tbody, data, column_info) {
  tbody.innerHTML = "";
  for (let row of data) {
    if (row.hidden) continue;

    let tr = document.createElement("tr");
    for (let col of column_info) {
      let td = document.createElement("td");
      if (col[2] === "date") {
        td.innerText = formatDate(row[col[0]]);
      } else if (col[2] === "money") {
        td.innerText = formatMoney(row[col[0]]);
      } else {
        td.innerText = row[col[0]];
      }

      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }

  // if empty, display empty message
  if (tbody.children.length === 0) {
    let tr = document.createElement("tr");
    let td = document.createElement("td");
    td.colSpan = column_info.length;
    td.className = "text-center text-muted";
    td.innerText = "No matching transactions found.";
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
}

function formatMoney(num) {
  if (typeof num === "string") num = parseFloat(num);
  let numFixed = num.toFixed(2);
  if (num < 0) {
    numFixed = numFixed.slice(1); // remove negative sign
  }

  // add commas
  let numDigits = numFixed.length - 3;
  if (numDigits > 3) {
    let numCommas = Math.floor((numDigits - 1) / 3);
    for (let i = 1; i <= numCommas; i++) {
      let idxToAdd = numDigits - 3 * i;
      numFixed = numFixed.slice(0, idxToAdd) + "," + numFixed.slice(idxToAdd);
    }
  }
  if (num < 0) {
    return "-$" + numFixed;
  } else {
    return "$" + numFixed;
  }
}

function getStats(data) {
  let totalSum = 0;
  let totalCount = 0;
  for (let row of data) {
    if (row.hidden) continue;
    totalSum += parseFloat(row.amount);
    totalCount += 1;
  }

  if (totalCount === 0) {
    return {
      sum: 0,
      count: 0,
      avg: 0,
    };
  } else {
    return {
      sum: totalSum,
      count: totalCount,
      avg: totalSum / totalCount,
    };
  }
}
