import { apiFetch } from "./client";

export function getOverview(date) {
  return apiFetch(date ? `/dashboard/overview?date=${date}` : "/dashboard/overview");
}

export function getMonthly(year, month) {
  return apiFetch(`/dashboard/monthly?year=${year}&month=${month}`);
}
