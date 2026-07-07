import { apiFetch } from "./client";

export function listExpenses(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiFetch(`/expenses${query ? `?${query}` : ""}`);
}

export function createExpense({ branchId, date, description, amount }) {
  return apiFetch("/expenses", {
    method: "POST",
    body: { branch_id: branchId, date, description, amount },
  });
}

export function deleteExpense(id, password) {
  return apiFetch(`/expenses/${id}`, { method: "DELETE", body: { password } });
}
