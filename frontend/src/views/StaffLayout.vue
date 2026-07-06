<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();

const navLinks = [
  { name: "staff-deliveries", label: "Deliveries" },
  { name: "staff-stock-count", label: "Stock Count" },
  { name: "staff-sales", label: "Sales" },
];

const menuOpen = ref(false);

watch(() => route.name, () => {
  menuOpen.value = false;
});

function goTo(name) {
  router.push({ name });
}

function onLogout() {
  auth.logout();
  router.push({ name: "login" });
}
</script>

<template>
  <div class="admin-shell">
    <header class="mobile-topbar">
      <div class="brand">
        <img src="/logo.png" alt="" class="brand-logo" />
        <span>Z.A. Company</span>
      </div>

      <button
        type="button"
        class="menu-toggle"
        :aria-expanded="menuOpen"
        :aria-label="menuOpen ? 'Close navigation menu' : 'Open navigation menu'"
        @click="menuOpen = !menuOpen"
      >
        <svg v-if="!menuOpen" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
        <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </header>

    <div v-if="menuOpen" class="sidebar-backdrop" @click="menuOpen = false"></div>

    <aside class="admin-sidebar" :class="{ 'menu-open': menuOpen }">
      <div class="sidebar-header">
        <div class="brand">
          <img src="/logo.png" alt="" class="brand-logo" />
          <span>Z.A. Company</span>
        </div>

        <button
          type="button"
          class="sidebar-close"
          aria-label="Close navigation menu"
          @click="menuOpen = false"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <nav>
        <button
          v-for="link in navLinks"
          :key="link.name"
          type="button"
          class="nav-link"
          :class="{ 'nav-link-active': route.name === link.name }"
          @click="goTo(link.name)"
        >
          {{ link.label }}
        </button>
      </nav>

      <button class="logout-btn" @click="onLogout">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        Log out
      </button>
    </aside>

    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-shell {
  min-height: 100vh;
  display: flex;
}

.admin-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--color-primary-dark);
  border-right: 3px solid var(--color-accent);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem 1.25rem;
  position: sticky;
  top: 0;
  height: 100vh;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.01em;
}

.brand-logo {
  width: 30px;
  height: 30px;
}

.mobile-topbar {
  display: none;
}

.sidebar-close {
  display: none;
}

.sidebar-backdrop {
  display: none;
}

.admin-sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.admin-sidebar .nav-link {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  padding: 0.6rem 0.9rem;
  border-radius: 8px;
  font-size: 0.92rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.admin-sidebar .nav-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.admin-sidebar .nav-link-active,
.admin-sidebar .nav-link-active:hover {
  color: var(--color-primary-dark);
  background: var(--color-accent);
  font-weight: 600;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.35);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  margin-top: auto;
}

.logout-btn:hover {
  background: var(--color-danger);
  border-color: var(--color-danger);
}

.admin-content {
  flex: 1;
  padding: 2.5rem 2rem;
  max-width: 1100px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 720px) {
  .admin-shell {
    flex-direction: column;
  }

  .mobile-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    position: sticky;
    top: 0;
    background: var(--color-primary-dark);
    border-bottom: 3px solid var(--color-accent);
    padding: 0.85rem 1rem;
    z-index: 50;
    transform: translateZ(0);
    -webkit-transform: translateZ(0);
  }

  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    flex-shrink: 0;
    padding: 0;
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 8px;
  }

  .menu-toggle:hover {
    background: rgba(255, 255, 255, 0.18);
  }

  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 40;
  }

  .admin-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 240px;
    max-width: 80vw;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    z-index: 45;
  }

  .admin-sidebar.menu-open {
    transform: translateX(0);
  }

  .sidebar-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    flex-shrink: 0;
    padding: 0;
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 8px;
  }

  .sidebar-close:hover {
    background: var(--color-danger);
    border-color: var(--color-danger);
  }

  .admin-content {
    padding: 1.5rem 1rem;
  }
}
</style>
