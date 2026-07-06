import { apiFetch } from "./client";

export function getTotpStatus() {
  return apiFetch("/settings/totp");
}

export function setupTotp() {
  return apiFetch("/settings/totp/setup", { method: "POST" });
}

export function enableTotp(secret, code) {
  return apiFetch("/settings/totp/enable", { method: "POST", body: { secret, code } });
}

export function disableTotp(password) {
  return apiFetch("/settings/totp/disable", { method: "POST", body: { password } });
}
