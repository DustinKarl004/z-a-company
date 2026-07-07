<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  modelValue: { type: [String, Number], default: "" },
  options: { type: Array, required: true },
  placeholder: { type: String, default: "Select..." },
  id: { type: String, default: "" },
  creatable: { type: Boolean, default: false },
  searchable: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "create"]);

const open = ref(false);
const root = ref(null);
const triggerRef = ref(null);
const dropdownRef = ref(null);
const searchRef = ref(null);
const highlighted = ref(-1);
const query = ref("");
const dropdownStyle = ref({});

function optionValue(option) {
  return option && typeof option === "object" ? option.value : option;
}

function optionLabel(option) {
  return option && typeof option === "object" ? option.label : option;
}

function optionGroup(option) {
  return option && typeof option === "object" ? option.group : undefined;
}

const selectedIndex = computed(() => props.options.findIndex((o) => optionValue(o) === props.modelValue));

const selectedLabel = computed(() => {
  if (props.creatable) return props.modelValue || "";
  const idx = selectedIndex.value;
  return idx >= 0 ? optionLabel(props.options[idx]) : "";
});

const filteredOptions = computed(() => {
  if (!(props.creatable || props.searchable) || !query.value.trim()) return props.options;
  const term = query.value.trim().toLowerCase();
  return props.options.filter((o) => optionLabel(o).toLowerCase().includes(term));
});

function showGroupHeader(idx) {
  const opts = filteredOptions.value;
  const g = optionGroup(opts[idx]);
  if (g === undefined) return false;
  return idx === 0 || optionGroup(opts[idx - 1]) !== g;
}

const canCreate = computed(() => {
  if (!props.creatable) return false;
  const term = query.value.trim();
  if (!term) return false;
  return !props.options.some((o) => optionLabel(o).toLowerCase() === term.toLowerCase());
});

function updatePosition() {
  const el = triggerRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const spaceBelow = window.innerHeight - rect.bottom;
  const openUpward = spaceBelow < 260 && rect.top > spaceBelow;
  dropdownStyle.value = {
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    ...(openUpward ? { bottom: `${window.innerHeight - rect.top + 6}px` } : { top: `${rect.bottom + 6}px` }),
  };
}

function onReposition() {
  if (open.value) updatePosition();
}

async function toggle() {
  if (open.value) {
    close();
    return;
  }
  query.value = "";
  open.value = true;
  highlighted.value = selectedIndex.value;
  await nextTick();
  updatePosition();
  if (props.creatable || props.searchable) searchRef.value?.focus();
}

function close() {
  open.value = false;
}

function choose(option) {
  emit("update:modelValue", optionValue(option));
  close();
}

function createOption() {
  const value = query.value.trim();
  if (!value) return;
  emit("create", value);
  emit("update:modelValue", value);
  close();
}

function onTriggerKeydown(e) {
  if (!open.value) {
    if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
      e.preventDefault();
      toggle();
    }
    return;
  }
  if (e.key === "Escape") {
    e.preventDefault();
    close();
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    highlighted.value = Math.min(highlighted.value + 1, props.options.length - 1);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    highlighted.value = Math.max(highlighted.value - 1, 0);
  } else if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    if (highlighted.value >= 0) choose(props.options[highlighted.value]);
  }
}

function onSearchKeydown(e) {
  const total = filteredOptions.value.length + (canCreate.value ? 1 : 0);
  if (e.key === "Escape") {
    e.preventDefault();
    close();
    triggerRef.value?.focus();
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    highlighted.value = Math.min(highlighted.value + 1, total - 1);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    highlighted.value = Math.max(highlighted.value - 1, 0);
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (highlighted.value >= 0 && highlighted.value < filteredOptions.value.length) {
      choose(filteredOptions.value[highlighted.value]);
    } else if (canCreate.value) {
      createOption();
    }
  }
}

watch(query, () => {
  highlighted.value = 0;
});

function onClickOutside(e) {
  if (root.value?.contains(e.target)) return;
  if (dropdownRef.value?.contains(e.target)) return;
  close();
}

watch(open, (isOpen) => {
  if (isOpen) {
    document.addEventListener("mousedown", onClickOutside);
    window.addEventListener("resize", onReposition);
    window.addEventListener("scroll", onReposition, true);
  } else {
    document.removeEventListener("mousedown", onClickOutside);
    window.removeEventListener("resize", onReposition);
    window.removeEventListener("scroll", onReposition, true);
  }
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onClickOutside);
  window.removeEventListener("resize", onReposition);
  window.removeEventListener("scroll", onReposition, true);
});
</script>

<template>
  <div ref="root" class="custom-select" :class="{ open }">
    <button
      :id="id"
      ref="triggerRef"
      type="button"
      class="custom-select-trigger"
      :class="{ placeholder: !modelValue }"
      @click="toggle"
      @keydown="onTriggerKeydown"
    >
      <span>{{ selectedLabel || placeholder }}</span>
      <svg class="chevron" width="12" height="8" viewBox="0 0 12 8" fill="none">
        <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <Teleport to="body">
      <div v-if="open" ref="dropdownRef" class="custom-select-dropdown" :style="dropdownStyle">
        <div v-if="creatable || searchable" class="custom-select-search">
          <input
            ref="searchRef"
            v-model="query"
            type="text"
            :placeholder="creatable ? 'Search or type to add' : 'Search...'"
            @keydown="onSearchKeydown"
          />
        </div>
        <ul class="custom-select-options" role="listbox">
          <template v-for="(option, idx) in filteredOptions" :key="optionValue(option)">
            <li v-if="showGroupHeader(idx)" class="custom-select-group-header">{{ optionGroup(option) }}</li>
            <li
              role="option"
              class="custom-select-option"
              :class="{ selected: optionValue(option) === modelValue, highlighted: idx === highlighted }"
              @mousedown.prevent="choose(option)"
              @mouseenter="highlighted = idx"
            >
              <span>{{ optionLabel(option) }}</span>
              <svg v-if="optionValue(option) === modelValue" class="check" width="12" height="10" viewBox="0 0 12 10" fill="none">
                <path d="M1 5L4.5 8.5L11 1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </li>
          </template>
          <li
            v-if="canCreate"
            class="custom-select-option custom-select-create"
            :class="{ highlighted: highlighted === filteredOptions.length }"
            @mousedown.prevent="createOption"
            @mouseenter="highlighted = filteredOptions.length"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 1V11M1 6H11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
            </svg>
            <span>Add "{{ query.trim() }}"</span>
          </li>
          <li v-if="creatable && !filteredOptions.length && !canCreate" class="custom-select-empty">
            Type to add an option
          </li>
        </ul>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.custom-select {
  position: relative;
}

.custom-select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-family: inherit;
  font-size: 0.95rem;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  text-align: left;
}

.custom-select-trigger span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-select-trigger.placeholder {
  color: var(--color-text-muted);
}

.custom-select-trigger:hover {
  border-color: var(--color-primary);
}

.custom-select.open .custom-select-trigger {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-soft);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-muted);
  transition: transform 0.15s ease;
}

.custom-select.open .chevron {
  transform: rotate(180deg);
  color: var(--color-primary);
}

.custom-select-dropdown {
  position: fixed;
  z-index: 200;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
  overflow: hidden;
  animation: select-pop 0.12s ease;
}

@keyframes select-pop {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.custom-select-search {
  flex-shrink: 0;
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.custom-select-search input {
  width: 100%;
  padding: 0.45rem 0.6rem;
  font-size: 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: 7px;
  background: var(--color-bg);
  color: var(--color-text);
}

.custom-select-search input:focus {
  border-color: var(--color-primary);
}

.custom-select-options {
  margin: 0;
  padding: 0.35rem;
  list-style: none;
  max-height: 220px;
  overflow-y: auto;
}

.custom-select-options::-webkit-scrollbar {
  width: 8px;
}

.custom-select-options::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 999px;
}

.custom-select-group-header {
  padding: 0.5rem 0.65rem 0.3rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.custom-select-group-header:not(:first-child) {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.55rem;
}

.custom-select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.55rem 0.65rem;
  border-radius: 7px;
  font-size: 0.9rem;
  color: var(--color-text);
  cursor: pointer;
}

.custom-select-option + .custom-select-option {
  margin-top: 1px;
}

.custom-select-option.highlighted {
  background: var(--color-primary-soft);
}

.custom-select-option.selected {
  color: var(--color-primary);
  font-weight: 600;
}

.custom-select-option .check {
  flex-shrink: 0;
  color: var(--color-primary);
}

.custom-select-create {
  color: var(--color-primary);
  border: 1px dashed var(--color-border);
}

.custom-select-create span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-select-create.highlighted {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}

.custom-select-empty {
  padding: 0.75rem 0.65rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  text-align: center;
}
</style>
