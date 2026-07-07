<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { listBranches } from "../api/branches";
import { ApiError } from "../api/client";
import { createExpense, deleteExpense, listExpenses } from "../api/expenses";
import { listSales } from "../api/sales";
import CustomSelect from "../components/CustomSelect.vue";
import ConfirmDeleteModal from "../components/ConfirmDeleteModal.vue";
import Icon from "../components/Icon.vue";

const today = new Date().toISOString().slice(0, 10);

const branches = ref([]);
const selectedDate = ref(today);
const selectedBranchId = ref("");

const expenses = ref([]);
const sales = ref([]);
const loading = ref(true);
const error = ref("");

const branchOptions = computed(() => [
  { label: "All branches", value: "" },
  ...branches.value.map((b) => ({ label: b.name, value: b.id })),
]);

const formBranchOptions = computed(() => branches.value.map((b) => ({ label: b.name, value: b.id })));

function branchName(id) {
  return branches.value.find((b) => b.id === id)?.name || "—";
}

function peso(amount) {
  return `₱${amount.toFixed(2)}`;
}

const totalSales = computed(() => sales.value.reduce((sum, s) => sum + s.amount, 0));
const totalExpenses = computed(() => expenses.value.reduce((sum, e) => sum + e.amount, 0));
const netProfit = computed(() => totalSales.value - totalExpenses.value);

const expenseForm = ref({ branchId: "", description: "", amount: "" });
const submitting = ref(false);

async function refresh() {
  loading.value = true;
  error.value = "";
  const params = { date: selectedDate.value };
  if (selectedBranchId.value) params.branch_id = selectedBranchId.value;
  try {
    [expenses.value, sales.value] = await Promise.all([listExpenses(params), listSales(params)]);
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not load data" : "Could not load data";
  } finally {
    loading.value = false;
  }
}

async function submitExpense() {
  error.value = "";
  submitting.value = true;
  try {
    await createExpense({
      branchId: expenseForm.value.branchId,
      date: selectedDate.value,
      description: expenseForm.value.description,
      amount: Number(expenseForm.value.amount),
    });
    expenseForm.value = { branchId: "", description: "", amount: "" };
    await refresh();
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not add expense" : "Could not add expense";
  } finally {
    submitting.value = false;
  }
}

const deleteTarget = ref(null);
const deleteModalError = ref("");
const deleting = ref(false);

function onDelete(expense) {
  deleteModalError.value = "";
  deleteTarget.value = expense;
}

function cancelDelete() {
  deleteTarget.value = null;
}

async function confirmDelete(password) {
  const expense = deleteTarget.value;
  deleteModalError.value = "";
  deleting.value = true;
  try {
    await deleteExpense(expense.id, password);
    deleteTarget.value = null;
    await refresh();
  } catch (e) {
    deleteModalError.value =
      e instanceof ApiError ? e.detail || "Could not delete expense" : "Could not delete expense";
  } finally {
    deleting.value = false;
  }
}

onMounted(async () => {
  branches.value = await listBranches();
  await refresh();
});

watch([selectedDate, selectedBranchId], refresh);
</script>

<template>
  <div class="page-header">
    <div>
      <h1>Expenses</h1>
      <p class="page-subtitle">Daily sales, bills, and net profit per branch.</p>
    </div>
    <div class="header-filters">
      <input v-model="selectedDate" type="date" />
      <CustomSelect v-model="selectedBranchId" :options="branchOptions" placeholder="All branches" />
    </div>
  </div>

  <p v-if="error" class="error-message top-error">{{ error }}</p>

  <div class="stat-row">
    <div class="card stat-card">
      <span class="stat-label">Sales</span>
      <span class="stat-value">{{ peso(totalSales) }}</span>
    </div>
    <div class="card stat-card">
      <span class="stat-label">Expenses</span>
      <span class="stat-value">{{ peso(totalExpenses) }}</span>
    </div>
    <div class="card stat-card" :class="{ 'stat-card-alert': netProfit < 0 }">
      <span class="stat-label">Net Profit</span>
      <span class="stat-value">{{ peso(netProfit) }}</span>
    </div>
  </div>

  <section class="card entry-section">
    <h2 class="card-title">Add a bill / expense</h2>
    <form class="entry-form" @submit.prevent="submitExpense">
      <div class="field">
        <label for="expense-branch">Branch</label>
        <CustomSelect
          id="expense-branch"
          v-model="expenseForm.branchId"
          :options="formBranchOptions"
          placeholder="Select a branch"
        />
      </div>
      <div class="field">
        <label for="expense-description">Description</label>
        <input id="expense-description" v-model="expenseForm.description" placeholder="e.g. Ice, LPG, electric bill" required />
      </div>
      <div class="field">
        <label for="expense-amount">Amount</label>
        <input id="expense-amount" v-model="expenseForm.amount" type="number" min="0" step="any" placeholder="e.g. 500" required />
      </div>
      <button type="submit" class="btn-icon" :disabled="submitting || !expenseForm.branchId">
        <Icon name="plus" :size="16" /> {{ submitting ? "Saving..." : "Add expense" }}
      </button>
    </form>
  </section>

  <ConfirmDeleteModal
    :open="!!deleteTarget"
    :title="`Delete &quot;${deleteTarget?.description}&quot;?`"
    message="This cannot be undone."
    :loading="deleting"
    :error="deleteModalError"
    @confirm="confirmDelete"
    @cancel="cancelDelete"
  />

  <p v-if="loading" class="state-message">Loading...</p>

  <template v-else>
    <div v-if="!expenses.length" class="card state-card">
      <div class="empty-state">
        <p>No expenses logged for this day.</p>
        <p class="empty-hint">Use the form above to log the first bill.</p>
      </div>
    </div>

    <ul v-else class="entry-list">
      <li v-for="e in expenses" :key="e.id" class="entry-item">
        <div class="entry-main">
          <div class="entry-name">{{ e.description }}</div>
          <span class="category-chip">{{ branchName(e.branch_id) }}</span>
        </div>
        <div class="entry-value">₱{{ e.amount.toFixed(2) }}</div>
        <button type="button" class="secondary danger btn-icon" @click="onDelete(e)">
          <Icon name="trash" :size="14" /> Delete
        </button>
      </li>
    </ul>
  </template>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
}

.page-header h1 {
  font-size: 1.5rem;
  margin-bottom: 0.35rem;
}

.page-subtitle {
  color: var(--color-text-muted);
  margin: 0;
}

.header-filters {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.header-filters input[type="date"] {
  width: auto;
}

.top-error {
  text-align: center;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 1.5rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-value {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text);
}

.stat-card-alert .stat-value {
  color: var(--color-danger);
}

.card-title {
  font-size: 0.95rem;
  margin-bottom: 1.1rem;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.entry-section {
  margin-bottom: 1.25rem;
}

.entry-form {
  display: grid;
  grid-template-columns: 1fr 1.4fr 1fr;
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

.state-message {
  text-align: center;
  color: var(--color-text-muted);
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

.entry-item .danger {
  flex-shrink: 0;
  font-size: 0.82rem;
  padding: 0.4rem 0.7rem;
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.entry-item .danger:hover {
  background: rgba(255, 77, 77, 0.1);
}

@media (max-width: 560px) {
  .stat-row {
    grid-template-columns: 1fr;
  }

  .entry-form {
    grid-template-columns: 1fr;
  }

  .entry-item {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
