<script setup>
import { onMounted, ref } from "vue";
import { listBranches } from "../api/branches";
import { createStaff, listStaff, updateStaff } from "../api/staff";
import { ApiError } from "../api/client";

const staff = ref([]);
const branches = ref([]);
const loading = ref(true);
const submitting = ref(false);
const error = ref("");

const form = ref({ name: "", email: "", password: "", branchId: "" });

function branchName(id) {
  return branches.value.find((b) => b.id === id)?.name || "—";
}

function initials(name) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

async function refresh() {
  loading.value = true;
  [staff.value, branches.value] = await Promise.all([listStaff(), listBranches()]);
  loading.value = false;
}

async function onSubmit() {
  error.value = "";
  submitting.value = true;
  try {
    await createStaff(form.value);
    form.value = { name: "", email: "", password: "", branchId: "" };
    await refresh();
  } catch (e) {
    error.value = e instanceof ApiError ? e.detail || "Could not create staff" : "Could not create staff";
  } finally {
    submitting.value = false;
  }
}

async function toggleActive(member) {
  await updateStaff(member.id, { is_active: !member.is_active });
  await refresh();
}

onMounted(refresh);
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Staff</h1>
        <p class="page-subtitle">Staff accounts, scoped to a single branch each.</p>
      </div>
      <span class="count-chip">{{ staff.length }} {{ staff.length === 1 ? "member" : "members" }}</span>
    </div>

    <form class="card new-staff" @submit.prevent="onSubmit">
      <h2 class="card-title">Add a staff member</h2>
      <div class="new-staff-grid">
        <div class="field">
          <label for="staff-name">Name</label>
          <input id="staff-name" v-model="form.name" required placeholder="Jane Dela Cruz" />
        </div>
        <div class="field">
          <label for="staff-email">Email</label>
          <input id="staff-email" v-model="form.email" type="email" required placeholder="jane@za-company.com" />
        </div>
        <div class="field">
          <label for="staff-password">Password</label>
          <input id="staff-password" v-model="form.password" type="password" required minlength="8" placeholder="At least 8 characters" />
        </div>
        <div class="field">
          <label for="staff-branch">Branch</label>
          <select id="staff-branch" v-model="form.branchId" required>
            <option disabled value="">Select a branch</option>
            <option v-for="b in branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>
      </div>
      <button type="submit" :disabled="submitting">{{ submitting ? "Adding..." : "Add staff" }}</button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>

    <div class="card table-card">
      <table v-if="!loading && staff.length">
        <thead>
          <tr>
            <th>Name</th>
            <th>Branch</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id">
            <td>
              <div class="person-cell">
                <span class="avatar">{{ initials(s.name) }}</span>
                <div>
                  <div class="primary-cell">{{ s.name }}</div>
                  <div class="secondary-cell">{{ s.email }}</div>
                </div>
              </div>
            </td>
            <td>{{ branchName(s.branch_id) }}</td>
            <td>
              <span class="badge" :class="s.is_active ? 'active' : 'inactive'">
                {{ s.is_active ? "Active" : "Inactive" }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="secondary" @click="toggleActive(s)">
                {{ s.is_active ? "Deactivate" : "Activate" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="loading" class="state-message">Loading staff...</p>
      <div v-else class="empty-state">
        <p>No staff yet.</p>
        <p class="empty-hint">Add a branch first, then create staff accounts for it above.</p>
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

.new-staff-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 0.25rem;
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

.person-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.primary-cell {
  font-weight: 600;
  color: var(--color-primary-dark);
}

.secondary-cell {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.actions-cell {
  text-align: right;
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

@media (max-width: 640px) {
  .new-staff-grid {
    grid-template-columns: 1fr;
  }
}
</style>
