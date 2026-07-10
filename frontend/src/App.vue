<template>
  <router-view />
  <div v-if="showUpdateBanner" class="update-banner">
    <span>A new version of the app is available.</span>
    <button type="button" @click="reload">Refresh now</button>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { startVersionCheck } from './utils/versionCheck'

// If an update is pending and no one has touched the page for this long,
// it's safe to assume nothing is mid-entry, so we reload for them.
const IDLE_RELOAD_MS = 2 * 60 * 1000
const IDLE_CHECK_INTERVAL_MS = 5_000
const ACTIVITY_EVENTS = ['click', 'keydown', 'touchstart', 'input']

const showUpdateBanner = ref(false)
let stopVersionCheck = () => {}
let idleCheckId = null
let updateAvailable = false
let lastActivityAt = Date.now()

function reload() {
  window.location.reload()
}

function markActivity() {
  lastActivityAt = Date.now()
}

onMounted(() => {
  ACTIVITY_EVENTS.forEach((event) => window.addEventListener(event, markActivity, { passive: true }))

  stopVersionCheck = startVersionCheck(() => {
    if (updateAvailable) return
    updateAvailable = true
    showUpdateBanner.value = true
    idleCheckId = setInterval(() => {
      if (Date.now() - lastActivityAt >= IDLE_RELOAD_MS) {
        reload()
      }
    }, IDLE_CHECK_INTERVAL_MS)
  })
})

onUnmounted(() => {
  stopVersionCheck()
  ACTIVITY_EVENTS.forEach((event) => window.removeEventListener(event, markActivity))
  if (idleCheckId) clearInterval(idleCheckId)
})
</script>

<style scoped>
.update-banner {
  position: fixed;
  left: 16px;
  right: 16px;
  bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  max-width: 420px;
  margin: 0 auto;
  box-sizing: border-box;
  z-index: 9999;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #1f2937;
  color: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  font-size: 14px;
}

.update-banner span {
  flex: 1 1 auto;
  min-width: 0;
}

.update-banner button {
  flex: 0 0 auto;
  background: #fff;
  color: #1f2937;
  border: none;
  border-radius: 6px;
  padding: 8px 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
</style>
