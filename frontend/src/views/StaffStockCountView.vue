<script setup>
import { computed, onMounted, ref } from "vue";
import { ApiError } from "../api/client";
import { listStockItems } from "../api/stockItems";
import { createStockCount, listStockCounts, updateStockCount } from "../api/stockCounts";
import CustomSelect from "../components/CustomSelect.vue";
import Icon from "../components/Icon.vue";

const today = new Date().toISOString().slice(0, 10);
const todayLabel = new Date().toLocaleDateString(undefined, {
  weekday: "long",
  month: "long",
  day: "numeric",
});

const categoryOrder = [
  "Meats",
  "Side Dishes / Banchan",
  "Rice & Staples",
  "Sauces & Condiments",
  "Drinks",
  "Consumables/Supplies",
];

function categoryRank(category) {
  if (!category) return categoryOrder.length;
  const idx = categoryOrder.findIndex((c) => c.toLowerCase() === category.toLowerCase());
  return idx === -1 ? categoryOrder.length : idx;
}

const stockItems = ref([]);
const counts = ref([]);
const loading = ref(true);
const error = ref("");
const search = ref("");

const countForm = ref({ itemId: "", quantityRemaining: "" });
const submitting = ref(false);

const itemOptions = computed(() =>
  stockItems.value
    .slice()
    .sort((a, b) => {
      const rankDiff = categoryRank(a.category) - categoryRank(b.category);
      return rankDiff !== 0 ? rankDiff : a.name.localeCompare(b.name);
    })
    .map((i) => ({ label: `${i.name} (${i.unit})`, value: i.id, group: i.category || "Uncategorized" }))
);

function itemName(id) {
  return stockItems.value.find((i) => i.id === id)?.name || "—";
}

function itemUnit(id) {
  return stockItems.value.find((i) => i.id === id)?.unit || "";
}

function itemCategory(id) {
  return stockItems.value.find((i) => i.id === id)?.category || "";
}

const filteredCounts = computed(() => {
  const term = search.value.trim().toLowerCase();
  if (!term) return counts.value;
  return counts.value.filter((c) => itemName(c.item_id).toLowerCase().includes(term));
});

async function refresh() {
  loading.value = true;
  [stockItems.value, counts.value] = await Promise.all([
    listStockItems(),
    listStockCounts({ date: today }),
  ]);
  loading.value = false;
}

async function submitCount() {
  error.value = "";
  submitting.value = true;
  try {
    await createStockCount({
      itemId: countForm.value.itemId,
      quantityRemaining: Number(countForm.value.quantityRemaining),
    });
    countForm.value = { itemId: "", quantityRemaining: "" };
    await refresh();
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not log count" : "Could not log count";
  } finally {
    submitting.value = false;
  }
}

const editingId = ref(null);
const editingQuantity = ref("");
const editError = ref("");
const savingEdit = ref(false);

function startEdit(count) {
  editingId.value = count.id;
  editingQuantity.value = count.quantity_remaining;
  editError.value = "";
}

function cancelEdit() {
  editingId.value = null;
  editError.value = "";
}

async function saveEdit(count) {
  editError.value = "";
  savingEdit.value = true;
  try {
    await updateStockCount(count.id, { quantity_remaining: Number(editingQuantity.value) });
    editingId.value = null;
    await refresh();
  } catch (e) {
    editError.value = e instanceof ApiError ? e.detail || "Could not update count" : "Could not update count";
  } finally {
    savingEdit.value = false;
  }
}

onMounted(refresh);
</script>

<template>
  <div class="page-header top-header">
    <div>
      <h1>End-of-day stock count</h1>
      <p class="page-subtitle">{{ todayLabel }} — you can edit anything logged today until midnight.</p>
    </div>
    <span v-if="!loading" class="count-chip"><Icon name="count" :size="14" /> {{ counts.length }} logged today</span>
  </div>

  <p v-if="error" class="error-message top-error">{{ error }}</p>
  <p v-if="loading" class="state-message">Loading...</p>

  <template v-else>
    <section class="card entry-section">
      <form class="entry-form" @submit.prevent="submitCount">
        <div class="field">
          <label for="count-item">Item</label>
          <CustomSelect id="count-item" v-model="countForm.itemId" :options="itemOptions" placeholder="Select an item" searchable />
        </div>
        <div class="field">
          <label for="count-qty">Quantity remaining</label>
          <input id="count-qty" v-model="countForm.quantityRemaining" type="number" min="0" step="any" placeholder="e.g. 12" required />
        </div>
        <button type="submit" class="btn-icon" :disabled="submitting || !countForm.itemId">
          <Icon name="plus" :size="16" /> {{ submitting ? "Saving..." : "Log count" }}
        </button>
      </form>
    </section>

    <div v-if="counts.length" class="card search-card">
      <div class="search-input">
        <Icon name="search" :size="15" class="search-icon" />
        <input v-model="search" placeholder="Search today's counts by item name" />
        <button v-if="search" type="button" class="search-clear" aria-label="Clear search" @click="search = ''">
          <Icon name="x" :size="13" />
        </button>
      </div>
    </div>

    <div v-if="!counts.length" class="card state-card">
      <div class="empty-state">
        <p>No stock count logged yet today.</p>
        <p class="empty-hint">Use the form above to log the first count.</p>
      </div>
    </div>
    <div v-else-if="!filteredCounts.length" class="card state-card">
      <div class="empty-state">
        <p>No counts match your search.</p>
      </div>
    </div>

    <ul v-else class="entry-list">
      <li v-for="c in filteredCounts" :key="c.id" class="entry-item">
        <template v-if="editingId === c.id">
          <div class="edit-row">
            <input v-model="editingQuantity" type="number" min="0" step="any" autofocus />
            <span class="edit-unit">{{ itemUnit(c.item_id) }}</span>
            <div class="edit-actions">
              <button type="button" class="secondary cancel" :disabled="savingEdit" @click="cancelEdit">Cancel</button>
              <button type="button" :disabled="savingEdit" @click="saveEdit(c)">{{ savingEdit ? "Saving..." : "Save" }}</button>
            </div>
          </div>
          <p v-if="editError" class="error-message">{{ editError }}</p>
        </template>
        <template v-else>
          <div class="entry-main">
            <div class="entry-name">{{ itemName(c.item_id) }}</div>
            <span v-if="itemCategory(c.item_id)" class="category-chip">{{ itemCategory(c.item_id) }}</span>
          </div>
          <div class="entry-value">{{ c.quantity_remaining }} {{ itemUnit(c.item_id) }}</div>
          <button type="button" class="secondary edit btn-icon" @click="startEdit(c)"><Icon name="edit" :size="14" /> Edit</button>
        </template>
      </li>
    </ul>
  </template>
</template>

<style scoped>
.top-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.page-header h1 {
  font-size: 1.5rem;
  margin-bottom: 0.35rem;
}

.page-subtitle {
  color: var(--color-text-muted);
  margin: 0;
}

.state-message {
  text-align: center;
  color: var(--color-text-muted);
}

.top-error {
  text-align: center;
}

.entry-section {
  margin-bottom: 1.25rem;
}

.entry-form {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 0.75rem 1rem;
  align-items: start;
}

.entry-form .field {
  margin-bottom: 0;
}

.entry-form button[type="submit"] {
  grid-column: 1 / -1;
  width: fit-content;
}

.search-card {
  padding: 0.85rem 1rem;
  margin-bottom: 1rem;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.65rem;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input input {
  width: 100%;
  padding-left: 2.1rem;
  padding-right: 2.1rem;
}

.search-clear {
  position: absolute;
  right: 0.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  background: transparent;
  color: var(--color-text-muted);
  border-radius: 50%;
}

.search-clear:hover {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.state-card {
  padding: 0;
}

.empty-state {
  padding: 2.5rem 1.5rem;
  text-align: center;
}

.empty-state p {
  margin: 0;
}

.empty-hint {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin-top: 0.35rem;
}

.entry-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.entry-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: var(--color-surface);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
  padding: 0.75rem 1rem;
  flex-wrap: wrap;
}

.entry-main {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1 1 180px;
  min-width: 0;
}

.entry-name {
  font-weight: 600;
  color: var(--color-text);
}

.category-chip {
  flex-shrink: 0;
  background: var(--color-bg);
  color: var(--color-text-muted);
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
}

.entry-value {
  font-size: 0.92rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.entry-item .edit {
  flex-shrink: 0;
  font-size: 0.82rem;
  padding: 0.4rem 0.7rem;
}

.edit-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex: 1;
  flex-wrap: wrap;
}

.edit-row input {
  width: 110px;
}

.edit-unit {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

@media (max-width: 560px) {
  .entry-form {
    grid-template-columns: 1fr;
  }

  .entry-item {
    flex-direction: column;
    align-items: stretch;
  }

  .edit-actions {
    margin-left: 0;
    justify-content: flex-end;
  }
}
</style>
