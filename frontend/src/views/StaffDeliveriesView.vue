<script setup>
import { onMounted, ref } from "vue";
import { ApiError } from "../api/client";
import { listStockItems } from "../api/stockItems";
import { createStockDelivery, listStockDeliveries } from "../api/stockDeliveries";

const today = new Date().toISOString().slice(0, 10);
const todayLabel = new Date().toLocaleDateString(undefined, {
  weekday: "long",
  month: "long",
  day: "numeric",
});

const stockItems = ref([]);
const deliveries = ref([]);
const loading = ref(true);
const error = ref("");

const deliveryForm = ref({ itemId: "", quantityDelivered: "", isShort: false });
const submitting = ref(false);

function itemName(id) {
  return stockItems.value.find((i) => i.id === id)?.name || "—";
}

function itemUnit(id) {
  return stockItems.value.find((i) => i.id === id)?.unit || "";
}

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

onMounted(refresh);
</script>

<template>
  <div class="page-header">
    <h1>Stock delivery</h1>
    <p class="page-subtitle">{{ todayLabel }} — you can edit anything logged today until midnight.</p>
  </div>

  <p v-if="error" class="error-message top-error">{{ error }}</p>
  <p v-if="loading" class="state-message">Loading...</p>

  <section v-else class="card entry-section">
    <form class="entry-form" @submit.prevent="submitDelivery">
      <select v-model="deliveryForm.itemId" required>
        <option disabled value="">Select an item</option>
        <option v-for="i in stockItems" :key="i.id" :value="i.id">{{ i.name }} ({{ i.unit }})</option>
      </select>
      <input v-model="deliveryForm.quantityDelivered" type="number" min="0" step="any" placeholder="Quantity delivered" required />
      <label class="checkbox-field">
        <input v-model="deliveryForm.isShort" type="checkbox" />
        Delivery was short / not enough
      </label>
      <button type="submit" :disabled="submitting">
        {{ submitting ? "Saving..." : "Log delivery" }}
      </button>
    </form>

    <ul class="entry-list" v-if="deliveries.length">
      <li v-for="d in deliveries" :key="d.id">
        <span>{{ itemName(d.item_id) }}</span>
        <span>{{ d.quantity_delivered }} {{ itemUnit(d.item_id) }}</span>
        <span v-if="d.is_short" class="badge inactive">Short</span>
      </li>
    </ul>
    <p v-else class="empty-hint">No deliveries logged yet today.</p>
  </section>
</template>

<style scoped>
.page-header {
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

.entry-form {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 1.25rem;
}

.entry-form select,
.entry-form input[type="number"] {
  width: 100%;
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

.checkbox-field input {
  width: auto;
}

.entry-form button {
  grid-column: 1 / -1;
  width: fit-content;
}

.entry-list {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-border);
}

.entry-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.92rem;
}

.entry-list li span:first-child {
  font-weight: 600;
  color: var(--color-text);
  flex: 1;
}

.empty-hint {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin: 0;
}

@media (max-width: 560px) {
  .entry-form {
    grid-template-columns: 1fr;
  }
}
</style>
