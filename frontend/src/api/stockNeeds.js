import { apiFetch, buildQuery } from "./client";

export function listStockNeeds(params = {}) {
  return apiFetch(`/stock-needs${buildQuery(params)}`);
}

export function createStockNeed({ branchId, itemId, date }) {
  return apiFetch("/stock-needs", {
    method: "POST",
    body: { branch_id: branchId, item_id: itemId, date },
  });
}

export function updateStockNeed(id, payload) {
  return apiFetch(`/stock-needs/${id}`, { method: "PATCH", body: payload });
}

export function deleteStockNeed(id) {
  return apiFetch(`/stock-needs/${id}`, { method: "DELETE" });
}
