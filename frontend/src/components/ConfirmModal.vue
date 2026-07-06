<script setup>
import Modal from "./Modal.vue";

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: "Are you sure?" },
  message: { type: String, default: "" },
  confirmLabel: { type: String, default: "Confirm" },
  loadingLabel: { type: String, default: "Working..." },
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
  variant: { type: String, default: "primary" },
});

const emit = defineEmits(["confirm", "cancel"]);

function onConfirm() {
  if (props.loading) return;
  emit("confirm");
}

function onCancel() {
  if (props.loading) return;
  emit("cancel");
}
</script>

<template>
  <Modal v-if="open" :title="title" @close="onCancel">
    <p v-if="message" class="modal-message">{{ message }}</p>

    <p v-if="error" class="error-message">{{ error }}</p>

    <div class="modal-actions">
      <button type="button" class="secondary" :disabled="loading" @click="onCancel">Cancel</button>
      <button
        type="button"
        :class="variant === 'danger' ? 'danger' : ''"
        :disabled="loading"
        @click="onConfirm"
      >
        {{ loading ? loadingLabel : confirmLabel }}
      </button>
    </div>
  </Modal>
</template>

<style scoped>
.modal-message {
  color: var(--color-text-muted);
  margin: 0 0 1.1rem;
}

.error-message {
  margin: -0.25rem 0 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
}

.modal-actions button {
  min-width: 100px;
}

.danger {
  background: var(--color-danger);
}

.danger:hover {
  background: var(--color-danger);
  opacity: 0.9;
}
</style>
