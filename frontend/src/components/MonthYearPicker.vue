<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  year: { type: Number, required: true },
  month: { type: Number, required: true },
});

const emit = defineEmits(["update:year", "update:month"]);

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const open = ref(false);
const root = ref(null);
const viewYear = ref(props.year);

watch(open, (isOpen) => {
  if (isOpen) viewYear.value = props.year;
});

function toggle() {
  open.value = !open.value;
}

function close() {
  open.value = false;
}

function prevYear() {
  viewYear.value -= 1;
}

function nextYear() {
  viewYear.value += 1;
}

function chooseMonth(idx) {
  emit("update:year", viewYear.value);
  emit("update:month", idx + 1);
  close();
}

function onClickOutside(e) {
  if (root.value && !root.value.contains(e.target)) close();
}

onMounted(() => document.addEventListener("mousedown", onClickOutside));
onBeforeUnmount(() => document.removeEventListener("mousedown", onClickOutside));
</script>

<template>
  <div ref="root" class="month-year-picker" :class="{ open }">
    <button type="button" class="picker-trigger" @click="toggle">
      <svg class="calendar-icon" width="15" height="15" viewBox="0 0 16 16" fill="none">
        <rect x="1.5" y="2.5" width="13" height="12" rx="2" stroke="currentColor" stroke-width="1.3" />
        <path d="M1.5 6H14.5" stroke="currentColor" stroke-width="1.3" />
        <path d="M4.5 1.2V3.6M11.5 1.2V3.6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
      </svg>
      <span>{{ MONTH_NAMES[month - 1] }} {{ year }}</span>
      <svg class="chevron" width="10" height="7" viewBox="0 0 12 8" fill="none">
        <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <div v-if="open" class="picker-panel">
      <div class="picker-year-row">
        <button type="button" class="year-nav" @click="prevYear">
          <svg width="9" height="14" viewBox="0 0 9 14" fill="none">
            <path d="M7.5 1L1.5 7L7.5 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
        <span class="picker-year">{{ viewYear }}</span>
        <button type="button" class="year-nav" @click="nextYear">
          <svg width="9" height="14" viewBox="0 0 9 14" fill="none">
            <path d="M1.5 1L7.5 7L1.5 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>
      <div class="picker-month-grid">
        <button
          v-for="(label, idx) in MONTH_LABELS"
          :key="label"
          type="button"
          class="picker-month"
          :class="{ selected: viewYear === year && idx + 1 === month }"
          @click="chooseMonth(idx)"
        >
          {{ label }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.month-year-picker {
  position: relative;
}

.picker-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: inherit;
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}

.picker-trigger:hover {
  border-color: var(--color-primary);
}

.month-year-picker.open .picker-trigger {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}

.calendar-icon {
  flex-shrink: 0;
  color: var(--color-text-muted);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-muted);
  transition: transform 0.15s ease;
}

.month-year-picker.open .chevron {
  transform: rotate(180deg);
  color: var(--color-primary);
}

.picker-panel {
  position: absolute;
  z-index: 20;
  top: calc(100% + 8px);
  right: 0;
  width: 240px;
  padding: 0.85rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  box-shadow: var(--shadow);
}

.picker-year-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.picker-year {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-text);
}

.year-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--color-text-muted);
}

.year-nav:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-text);
}

.picker-month-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.4rem;
}

.picker-month {
  padding: 0.45rem 0;
  border-radius: 6px;
  background: transparent;
  color: var(--color-text);
  font-size: 0.8rem;
  font-weight: 600;
}

.picker-month:hover {
  background: rgba(255, 255, 255, 0.06);
}

.picker-month.selected {
  background: var(--color-primary);
  color: #fff;
}
</style>
