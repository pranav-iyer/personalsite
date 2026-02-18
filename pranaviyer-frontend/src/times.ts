const MS_PER_HOUR = 1000 * 60 * 60;
const MS_PER_MINUTE = 1000 * 60;

export function formatDelta(startTime: Date, endTime: Date) {
  let ms = endTime.getTime() - startTime.getTime();
  let hours = Math.floor(ms / MS_PER_HOUR);
  let minutes = Math.floor((ms - MS_PER_HOUR * hours) / MS_PER_MINUTE);
  return `${hours} hour${hours != 1 ? "s" : ""}, ${minutes} minute${minutes != 1 ? "s" : ""}`;
}

export function addDays(d: Date, n: number) {
  let newDate = structuredClone(d);
  newDate.setDate(d?.getDate() + n);
  return newDate;
}
