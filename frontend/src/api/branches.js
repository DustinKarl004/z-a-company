import { apiFetch } from "./client";

export function listBranches() {
  return apiFetch("/branches");
}

export function createBranch(name) {
  return apiFetch("/branches", { method: "POST", body: { name } });
}

export function updateBranch(id, name) {
  return apiFetch(`/branches/${id}`, { method: "PATCH", body: { name } });
}

export function deleteBranch(id, password) {
  return apiFetch(`/branches/${id}`, { method: "DELETE", body: { password } });
}
