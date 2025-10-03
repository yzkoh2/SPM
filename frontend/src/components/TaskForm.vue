<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">{{ formTitle }}</h2>
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
        <input v-model="editableTask.title" type="text" required class="w-full form-input" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea v-model="editableTask.description" rows="3" class="w-full form-input"></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
        <input v-model="editableTask.deadline" type="datetime-local" class="w-full form-input" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
        <select v-model="editableTask.status" class="w-full form-select">
          <option value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
      </div>

      <div class="flex justify-end space-x-3 pt-2">
        <button type="button" @click="emit('cancel')" class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
          Cancel
        </button>
        <button type="submit" :disabled="isSubmitting" class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
          {{ isSubmitting ? 'Saving...' : submitButtonText }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  task: {
    type: Object,
    default: () => ({ title: '', description: '', deadline: '', status: 'Unassigned' })
  },
  mode: {
    type: String,
    default: 'create' // 'create' or 'edit'
  },
  isSubmitting: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['submit', 'cancel']);

const editableTask = ref({});

// When the component is mounted or the task prop changes, update the local state
const resetForm = () => {
  // Format deadline for the datetime-local input
  const deadline = props.task.deadline ? new Date(props.task.deadline).toISOString().slice(0, 16) : '';
  editableTask.value = { ...props.task, deadline };
};

onMounted(resetForm);
watch(() => props.task, resetForm, { deep: true });

const formTitle = computed(() => props.mode === 'edit' ? 'Edit Task' : 'Create New Task');
const submitButtonText = computed(() => props.mode === 'edit' ? 'Save Changes' : 'Create Task');

const handleSubmit = () => {
  // Convert deadline back to a standard format if it exists
  const submissionData = { ...editableTask.value };
  if (submissionData.deadline) {
    submissionData.deadline = new Date(submissionData.deadline).toISOString();
  }
  emit('submit', submissionData);
};
</script>

<style scoped>
</style>