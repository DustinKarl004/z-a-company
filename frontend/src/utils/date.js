import { getToday } from "../api/clock";

// Fallback only — used if the device can't reach the backend. Whenever
// possible, `fetchBusinessToday()` below asks the server instead, since it's
// the single source of truth and doesn't depend on the device's clock/timezone.
const FALLBACK_CUTOFF_HOUR = 6;

export function toLocalISO(d) {
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
}

export function parseLocalISO(s) {
  const [y, m, d] = s.split("-").map(Number);
  return new Date(y, m - 1, d);
}

// The current business day (not the raw calendar day) — before the cutoff
// hour, it's still "yesterday" as far as opening/closing stock is concerned.
// Fallback-only; prefer `fetchBusinessToday()`.
export function businessDay(cutoffHour = FALLBACK_CUTOFF_HOUR) {
  const d = new Date();
  if (d.getHours() < cutoffHour) {
    d.setDate(d.getDate() - 1);
  }
  return d;
}

export function todayLocalISO() {
  return toLocalISO(businessDay());
}

export function formatTime(d) {
  return d.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}

// The next moment the business day rolls over — today at the cutoff hour if
// that hasn't happened yet, otherwise tomorrow at the cutoff hour.
export function nextBusinessDayCutoff(cutoffHour = FALLBACK_CUTOFF_HOUR) {
  const now = new Date();
  const cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate(), cutoffHour, 0);
  if (now >= cutoff) {
    cutoff.setDate(cutoff.getDate() + 1);
  }
  return cutoff;
}

export function businessDayCutoffLabel(cutoffHour = FALLBACK_CUTOFF_HOUR) {
  const cutoff = nextBusinessDayCutoff(cutoffHour);
  const dateLabel = cutoff.toLocaleDateString(undefined, { month: "long", day: "numeric" });
  return `${formatTime(cutoff)}, ${dateLabel}`;
}

// The backend is the single source of truth for "what business day is it" —
// asking it avoids relying on the device's own (possibly wrong) clock/timezone
// right at the cutoff boundary. Falls back to local computation if unreachable.
export async function fetchBusinessToday() {
  try {
    const res = await getToday();
    return { date: parseLocalISO(res.date), cutoffHour: res.cutoff_hour };
  } catch {
    return { date: businessDay(), cutoffHour: FALLBACK_CUTOFF_HOUR };
  }
}
