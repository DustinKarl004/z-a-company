<script setup>
import { computed, onMounted, ref } from "vue";
import { ApiError } from "../api/client";
import { listStockItems } from "../api/stockItems";
import { createStockDelivery, listStockDeliveries, updateStockDelivery } from "../api/stockDeliveries";
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
const deliveries = ref([]);
const loading = ref(true);
const error = ref("");
const search = ref("");

const deliveryForm = ref({ itemId: "", quantityDelivered: "", isShort: false });
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

const filteredDeliveries = computed(() => {
  const term = search.value.trim().toLowerCase();
  if (!term) return deliveries.value;
  return deliveries.value.filter((d) => itemName(d.item_id).toLowerCase().includes(term));
});

async function refresh() {
  loading.value = true;
  [stockItems.value, deliveries.value] = await Promise.all([
    listStockItems(),
    listStockDeliveries({ date: today }),
  ]);
  loading.value = false;
}

async function submitDelivery() {
  error.value = "";
  submitting.value = true;
  try {
    await createStockDelivery({
      itemId: deliveryForm.value.itemId,
      quantityDelivered: Number(deliveryForm.value.quantityDelivered),
      isShort: deliveryForm.value.isShort,
    });
    deliveryForm.value = { itemId: "", quantityDelivered: "", isShort: false };
    await refresh();
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not log delivery" : "Could not log delivery";
  } finally {
    submitting.value = false;
  }
}

const editingId = ref(null);
const editingQuantity = ref("");
const editingIsShort = ref(false);
const editError = ref("");
const savingEdit = ref(false);

function startEdit(delivery) {
  editingId.value = delivery.id;
  editingQuantity.value = delivery.quantity_delivered;
  editingIsShort.value = delivery.is_short;
  editError.value = "";
}

function cancelEdit() {
  editingId.value = null;
  editError.value = "";
}

async function saveEdit(delivery) {
  editError.value = "";
  savingEdit.value = true;
  try {
    await updateStockDelivery(delivery.id, {
      quantity_delivered: Number(editingQuantity.value),
      is_short: editingIsShort.value,
    });
    editingId.value = null;
    await refresh();
  } catch (e) {
    editError.value = e instanceof ApiError ? e.detail || "Could not update delivery" : "Could not update delivery";
  } finally {
    savingEdit.value = false;
  }
}

onMounted(refresh);
</script>

<template>
  <div class="page-header top-header">
    <div>
      <h1>Stock delivery</h1>
      <p class="page-subtitle">{{ todayLabel }} — you can edit anything logged today until midnight.</p>
    </div>
    <span v-if="!loading" class="count-chip"><Icon name="count" :size="14" /> {{ deliveries.length }} logged today</span>
  </div>

  <p v-if="error" class="error-message top-error">{{ error }}</p>
  <p v-if="loading" class="state-message">Loading...</p>

  <template v-else>
    <section class="card entry-section">
      <form class="entry-form" @submit.prevent="submitDelivery">
        <div class="field">
          <label for="delivery-item">Item</label>
          <CustomSelect id="delivery-item" v-model="deliveryForm.itemId" :options="itemOptions" placeholder="Select an item" searchable />
        </div>
        <div class="field">
          <label for="delivery-qty">Quantity delivered</label>
          <input id="delivery-qty" v-model="deliveryForm.quantityDelivered" type="number" min="0" step="any" placeholder="e.g. 10" required />
        </div>
        <label class="checkbox-field">
          <input v-model="deliveryForm.isShort" type="checkbox" />
          Delivery was short / not enough
        </label>
        <button type="submit" class="btn-icon" :disabled="submitting || !deliveryForm.itemId">
          <Icon name="plus" :size="16" /> {{ submitting ? "Saving..." : "Log delivery" }}
        </button>
      </form>
    </section>

    <div v-if="deliveries.length" class="card search-card">
      <div class="search-input">
        <Icon name="search" :size="15" class="search-icon" />
        <input v-model="search" placeholder="Search today's deliveries by item name" />
        <button v-if="search" type="button" class="search-clear" aria-label="Clear search" @click="search = ''">
          <Icon name="x" :size="13" />
        </button>
      </div>
    </div>

    <div v-if="!deliveries.length" class="card state-card">
      <div class="empty-state">
        <p>No deliveries logged yet today.</p>
        <p class="empty-hint">Use the form above to log the first delivery.</p>
      </div>
    </div>
    <div v-else-if="!filteredDeliveries.length" class="card state-card">
      <div class="empty-state">
        <p>No deliveries match your search.</p>
      </div>
    </div>

    <ul v-else class="entry-list">
      <li v-for="d in filteredDeliveries" :key="d.id" class="entry-item">
        <template v-if="editingId === d.id">
          <div class="edit-row">
            <input v-model="editingQuantity" type="number" min="0" step="any" autofocus />
            <span class="edit-unit">{{ itemUnit(d.item_id) }}</span>
            <label class="checkbox-field inline">
              <input v-model="editingIsShort" type="checkbox" />
              Short
            </label>
            <div class="edit-actions">
              <button type="button" class="secondary cancel" :disabled="savingEdit" @click="cancelEdit">Cancel</button>
              <button type="button" :disabled="savingEdit" @click="saveEdit(d)">{{ savingEdit ? "Saving..." : "Save" }}</button>
            </div>
          </div>
          <p v-if="editError" class="error-message">{{ editError }}</p>
        </template>
        <template v-else>
          <div class="entry-main">
            <div class="entry-name">{{ itemName(d.item_id) }}</div>
            <span v-if="itemCategory(d.item_id)" class="category-chip">{{ itemCategory(d.item_id) }}</span>
            <span v-if="d.is_short" class="badge inactive">Short</span>
          </div>
          <div class="entry-value">{{ d.quantity_delivered }} {{ itemUnit(d.item_id) }}</div>
          <button type="button" class="secondary edit btn-icon" @click="startEdit(d)"><Icon name="edit" :size="14" /> Edit</button>
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

.checkbox-field {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text);
  margin: 0;
}

.checkbox-field.inline {
  flex-shrink: 0;
}

.checkbox-field input {
  width: auto;
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

.edit-row input[type="number"] {
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
