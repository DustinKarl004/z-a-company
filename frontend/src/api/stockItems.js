import { apiFetch } from "./client";

export function listStockItems() {
  return apiFetch("/stock-items");
}

export function createStockItem({ name, unit, price }) {
  return apiFetch("/stock-items", { method: "POST", body: { name, unit, price } });
}

export function updateStockItem(id, { name, unit, price }) {
  return apiFetch(`/stock-items/${id}`, { method: "PATCH", body: { name, unit, price } });
}

export function deleteStockItem(id, password) {
  return apiFetch(`/stock-items/${id}`, { method: "DELETE", body: { password } });
}
