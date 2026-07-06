<script setup>
import { computed, onMounted, ref } from "vue";
import { ApiError } from "../api/client";
import { listStockItems } from "../api/stockItems";
import { createSale, listSales } from "../api/sales";

const today = new Date().toISOString().slice(0, 10);
const todayLabel = new Date().toLocaleDateString(undefined, {
  weekday: "long",
  month: "long",
  day: "numeric",
});

const stockItems = ref([]);
const sales = ref([]);
const loading = ref(true);
const error = ref("");

const saleForm = ref({ itemId: "", quantitySold: "" });
const submitting = ref(false);

function itemName(id) {
  return stockItems.value.find((i) => i.id === id)?.name || "—";
}

function itemUnit(id) {
  return stockItems.value.find((i) => i.id === id)?.unit || "";
}

function itemPrice(id) {
  return stockItems.value.find((i) => i.id === id)?.price || 0;
}

const saleFormAmount = computed(() =>
  itemPrice(saleForm.value.itemId) * Number(saleForm.value.quantitySold || 0)
);

async function refresh() {
  loading.value = true;
  [stockItems.value, sales.value] = await Promise.all([
    listStockItems(),
    listSales({ date: today }),
  ]);
  loading.value = false;
}

async function submitSale() {
  error.value = "";
  submitting.value = true;
  try {
    await createSale({
      itemId: saleForm.value.itemId,
      quantitySold: Number(saleForm.value.quantitySold),
    });
    saleForm.value = { itemId: "", quantitySold: "" };
    await refresh();
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not log sale" : "Could not log sale";
  } finally {
    submitting.value = false;
  }
}

const totalSalesToday = computed(() => sales.value.reduce((sum, s) => sum + s.amount, 0));

onMounted(refresh);
</script>

<template>
  <div class="page-header">
    <h1>Sales</h1>
    <p class="page-subtitle">{{ todayLabel }} — you can edit anything logged today until midnight.</p>
  </div>

  <p v-if="error" class="error-message top-error">{{ error }}</p>
  <p v-if="loading" class="state-message">Loading...</p>

  <section v-else class="card entry-section">
    <form class="entry-form" @submit.prevent="submitSale">
      <select v-model="saleForm.itemId" required>
        <option disabled value="">Select an item</option>
        <option v-for="i in stockItems" :key="i.id" :value="i.id">{{ i.name }} ({{ i.unit }})</option>
      </select>
      <input v-model="saleForm.quantitySold" type="number" min="0" step="any" placeholder="Quantity sold" required />
      <p v-if="saleForm.itemId" class="amount-preview">Amount: ₱{{ saleFormAmount.toFixed(2) }}</p>
      <button type="submit" :disabled="submitting">
        {{ submitting ? "Saving..." : "Log sale" }}
      </button>
    </form>

    <ul class="entry-list" v-if="sales.length">
      <li v-for="s in sales" :key="s.id">
        <span>{{ itemName(s.item_id) }}</span>
        <span>{{ s.quantity_sold }} {{ itemUnit(s.item_id) }} — ₱{{ s.amount.toFixed(2) }}</span>
      </li>
    </ul>
    <p v-else class="empty-hint">No sales logged yet today.</p>
    <p v-if="sales.length" class="sales-total">Total sales today: ₱{{ totalSalesToday.toFixed(2) }}</p>
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

.amount-preview {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-muted);
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

.sales-total {
  margin: 0.75rem 0 0;
  font-weight: 700;
  color: var(--color-text);
  text-align: right;
}

@media (max-width: 560px) {
  .entry-form {
    grid-template-columns: 1fr;
  }
}
</style>
