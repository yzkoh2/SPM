<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-8">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">{{ title }}</h2>
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ isSubtask ? 'Subtask Title' : 'Task Title' }}
        </label>
        <input v-model="localData.title" type="text" required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
        <input v-model="localData.deadline" type="datetime-local"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea v-model="localData.description" rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="Describe the task in detail..."></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
        <select v-model="localData.status"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
          <option value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
      </div>

      <div class="flex justify-end space-x-3">
        <button type="button" @click="$emit('cancel')"
          class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors">
          Cancel
        </button>
        <button type="submit" :disabled="isSubmitting"
          class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors disabled:opacity-50">
          {{ isSubmitting ? submitButtonLoadingText : submitButtonText }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Create New Task'
  },
  isSubtask: {
    type: Boolean,
    default: false
  },
  isSubmitting: {
    type: Boolean,
    default: false
  },
  submitButtonText: {
    type: String,
    default: 'Create Task'
  },
  submitButtonLoadingText: {
    type: String,
    default: 'Creating...'
  }
})

const emit = defineEmits(['submit', 'cancel'])

const localData = ref({
  title: '',
  deadline: '',
  description: '',
  status: 'Unassigned'
})

const handleSubmit = () => {
  emit('submit', { ...localData.value })
  // Reset form after submission
  localData.value = {
    title: '',
    deadline: '',
    description: '',
    status: 'Unassigned'
  }
}
</script>