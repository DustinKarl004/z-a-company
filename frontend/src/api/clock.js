import { apiFetch } from "./client";

export function getToday() {
  return apiFetch("/clock/today");
}
