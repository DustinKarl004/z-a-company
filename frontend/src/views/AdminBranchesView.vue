<script setup>
import { onMounted, ref } from "vue";
import { createBranch, listBranches } from "../api/branches";
import { ApiError } from "../api/client";

const branches = ref([]);
const name = ref("");
const error = ref("");
const submitting = ref(false);
const loading = ref(true);

async function refresh() {
  loading.value = true;
  branches.value = await listBranches();
  loading.value = false;
}

async function onSubmit() {
  error.value = "";
  submitting.value = true;
  try {
    await createBranch(name.value);
    name.value = "";
    await refresh();
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not create branch" : "Could not create branch";
  } finally {
    submitting.value = false;
  }
}

onMounted(refresh);
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Branches</h1>
        <p class="page-subtitle">Every branch that can have its own staff and daily records.</p>
      </div>
      <span class="count-chip">{{ branches.length }} {{ branches.length === 1 ? "branch" : "branches" }}</span>
    </div>

    <form class="card new-branch" @submit.prevent="onSubmit">
      <h2 class="card-title">Add a branch</h2>
      <div class="new-branch-row">
        <div class="field">
          <label for="branch-name">Branch name</label>
          <input id="branch-name" v-model="name" required placeholder="e.g. Quezon City" />
        </div>
        <button type="submit" :disabled="submitting">{{ submitting ? "Adding..." : "Add branch" }}</button>
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>

    <div class="card table-card">
      <table v-if="!loading && branches.length">
        <thead>
          <tr>
            <th>Name</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in branches" :key="b.id">
            <td class="primary-cell">{{ b.name }}</td>
            <td>{{ new Date(b.created_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="loading" class="state-message">Loading branches...</p>
      <div v-else class="empty-state">
        <p>No branches yet.</p>
        <p class="empty-hint">Add your first branch above to start assigning staff to it.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
}

.page-header h1 {
  font-size: 1.6rem;
  margin-bottom: 0.35rem;
}

.page-subtitle {
  color: var(--color-text-muted);
  margin: 0;
}

.count-chip {
  flex-shrink: 0;
  background: rgba(15, 110, 110, 0.1);
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  white-space: nowrap;
}

.card {
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.05rem;
  margin-bottom: 1rem;
}

.new-branch-row {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
}

.new-branch-row .field {
  flex: 1;
  margin-bottom: 0;
}

.table-card {
  padding: 0;
  overflow: hidden;
}

.table-card table {
  margin: 0;
}

.table-card th,
.table-card td {
  padding: 0.85rem 1.5rem;
}

.table-card tbody tr:hover {
  background: var(--color-bg);
}

.primary-cell {
  font-weight: 600;
  color: var(--color-primary-dark);
}

.state-message {
  padding: 2rem 1.5rem;
  text-align: center;
  color: var(--color-text-muted);
  margin: 0;
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
</style>
