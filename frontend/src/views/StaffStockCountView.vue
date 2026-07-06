<script setup>
import { onMounted, ref } from "vue";
import { ApiError } from "../api/client";
import { listStockItems } from "../api/stockItems";
import { createStockCount, listStockCounts } from "../api/stockCounts";

const today = new Date().toISOString().slice(0, 10);
const todayLabel = new Date().toLocaleDateString(undefined, {
  weekday: "long",
  month: "long",
  day: "numeric",
});

const stockItems = ref([]);
const counts = ref([]);
const loading = ref(true);
const error = ref("");

const countForm = ref({ itemId: "", quantityRemaining: "" });
const submitting = ref(false);

function itemName(id) {
  return stockItems.value.find((i) => i.id === id)?.name || "—";
}

function itemUnit(id) {
  return stockItems.value.find((i) => i.id === id)?.unit || "";
}

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

onMounted(refresh);
</script>

<template>
  <div class="page-header">
    <h1>End-of-day stock count</h1>
    <p class="page-subtitle">{{ todayLabel }} — you can edit anything logged today until midnight.</p>
  </div>

  <p v-if="error" class="error-message top-error">{{ error }}</p>
  <p v-if="loading" class="state-message">Loading...</p>

  <section v-else class="card entry-section">
    <form class="entry-form" @submit.prevent="submitCount">
      <select v-model="countForm.itemId" required>
        <option disabled value="">Select an item</option>
        <option v-for="i in stockItems" :key="i.id" :value="i.id">{{ i.name }} ({{ i.unit }})</option>
      </select>
      <input v-model="countForm.quantityRemaining" type="number" min="0" step="any" placeholder="Quantity remaining" required />
      <button type="submit" :disabled="submitting">
        {{ submitting ? "Saving..." : "Log count" }}
      </button>
    </form>

    <ul class="entry-list" v-if="counts.length">
      <li v-for="c in counts" :key="c.id">
        <span>{{ itemName(c.item_id) }}</span>
        <span>{{ c.quantity_remaining }} {{ itemUnit(c.item_id) }}</span>
      </li>
    </ul>
    <p v-else class="empty-hint">No stock count logged yet today.</p>
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
