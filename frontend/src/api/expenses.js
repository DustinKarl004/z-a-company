import { apiFetch, buildQuery } from "./client";

export function listExpenses(params = {}) {
  return apiFetch(`/expenses${buildQuery(params)}`);
}

export function createExpense({ branchId, date, description, amount }) {
  return apiFetch("/expenses", {
    method: "POST",
    body: { branch_id: branchId, date, description, amount },
  });
}

export function deleteExpense(id) {
  return apiFetch(`/expenses/${id}`, { method: "DELETE" });
}

export function deleteMonthData(year, month, password) {
  return apiFetch(`/expenses/month${buildQuery({ year, month })}`, {
    method: "DELETE",
    body: { password },
  });
}
