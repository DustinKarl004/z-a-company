import { apiFetch } from "./client";

export function login(email, password, totpCode) {
  return apiFetch("/auth/login", {
    method: "POST",
    auth: false,
    body: { email, password, totp_code: totpCode || undefined },
  });
}
