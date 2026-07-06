<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { ApiError } from "../api/client";

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const showPassword = ref(false);

const auth = useAuthStore();
const router = useRouter();

async function onSubmit() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    router.push(auth.role === "admin" ? { name: "admin-branches" } : { name: "staff-home" });
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Login failed" : "Login failed";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <section class="left">
      <div class="left-inner">
        <img class="brand-logo" src="/logo.svg" alt="Z.A. Company" />
        <h1 class="brand-title">Z.A. Company</h1>
        <p class="brand-tagline">Stocks, sales, and profit — tracked per branch, every day.</p>
      </div>
    </section>

    <section class="right">
      <div class="auth-box">
        <div class="mobile-logo">
          <img class="mobile-logo-img" src="/logo.svg" alt="Z.A. Company" />
        </div>

        <div class="tab-sw">
          <button class="tab-btn active" type="button">sign in</button>
        </div>

        <form class="fp active" @submit.prevent="onSubmit">
          <div class="fg">
            <label for="email">Email address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              maxlength="254"
              autocomplete="email"
              placeholder="you@za-company.com"
              required
            />
          </div>

          <div class="fg">
            <label for="password">Password</label>
            <div class="inpw">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                class="tpw"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                @click="showPassword = !showPassword"
              >
                <svg v-if="showPassword" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
                <svg v-else width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </button>
            </div>
          </div>

          <button class="btn-p" type="submit" :disabled="loading">
            <span v-if="loading" class="spinner" aria-hidden="true"></span>
            {{ loading ? "Signing in..." : "Sign in" }}
          </button>

          <p v-if="error" class="error-message">{{ error }}</p>
        </form>
      </div>
    </section>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

.left {
  flex: 0.85;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  position: relative;
  overflow: hidden;
}

.left::before {
  content: "";
  position: absolute;
  width: 480px;
  height: 480px;
  border-radius: 50%;
  background: rgba(242, 169, 59, 0.12);
  top: -140px;
  right: -140px;
}

.left-inner {
  position: relative;
  z-index: 1;
  max-width: 380px;
  text-align: center;
}

.brand-logo {
  width: 96px;
  height: 96px;
  margin-bottom: 1.5rem;
  filter: drop-shadow(0 6px 18px rgba(0, 0, 0, 0.25));
}

.brand-title {
  color: #fff;
  font-size: 1.9rem;
  margin-bottom: 0.75rem;
}

.brand-tagline {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.05rem;
  line-height: 1.5;
  margin: 0;
}

.right {
  flex: 1.15;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: 3rem;
}

.auth-box {
  width: 100%;
  max-width: 420px;
}

.mobile-logo-img {
  display: block;
  width: 52px;
  height: 52px;
  margin: 0 auto 1.25rem;
}

.tab-sw {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.75rem;
}

.tab-btn {
  background: transparent;
  color: var(--color-text-muted);
  border: none;
  padding: 0.5rem 0.25rem;
  font-size: 1.05rem;
  font-weight: 600;
  text-transform: capitalize;
  border-bottom: 2px solid transparent;
  border-radius: 0;
}

.tab-btn:hover {
  background: transparent;
  color: var(--color-primary-dark);
}

.tab-btn.active {
  color: var(--color-primary-dark);
  border-bottom-color: var(--color-accent);
}

.fg {
  margin-bottom: 1.35rem;
}

.fg label {
  font-size: 0.9rem;
}

.fg input {
  width: 100%;
  padding: 0.75rem 0.85rem;
  font-size: 1.02rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.fg input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(15, 110, 110, 0.15);
}

.inpw {
  position: relative;
}

.inpw input {
  padding-right: 2.75rem;
}

.tpw {
  position: absolute;
  top: 50%;
  right: 0.35rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: transparent;
  color: var(--color-text-muted);
  border: none;
  border-radius: 6px;
  padding: 0;
}

.tpw:hover {
  background: rgba(15, 110, 110, 0.08);
  color: var(--color-primary);
}

.btn-p {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.75rem;
  padding: 0.85rem 1rem;
  font-size: 1.02rem;
  font-weight: 600;
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  text-align: center;
  margin-top: 1rem;
}

.mobile-logo {
  display: none;
}

@media (max-width: 860px) {
  .login-page {
    flex-direction: column;
  }

  .left {
    display: none;
  }

  .mobile-logo {
    display: block;
  }

  .right {
    padding: 1.5rem;
  }
}
</style>
