<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-8">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">{{ isSubtask ? 'Create New Subtask' : 'Create New Task' }}</h2>
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
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Priority</label>
        <input v-model="localData.priority" type="range" min="1" max="10"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
        <div class="flex justify-between text-xs text-gray-600 mt-1">
          <span v-for="n in 10" :key="n">{{ n }}</span>
        </div>
      </div>

      <div>
        <label class="flex items-center">
          <input v-model="localData.is_recurring" type="checkbox"
            class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          <span class="ml-2 text-sm text-gray-600">Is this a recurring task?</span>
        </label>
      </div>

      <div v-if="localData.is_recurring">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence Interval</label>
          <select v-model="localData.recurrence_interval"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div v-if="localData.recurrence_interval === 'custom'">
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence Days</label>
          <input v-model="localData.recurrence_days" type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence End Date</label>
          <input v-model="localData.recurrence_end_date" type="datetime-local"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
        </div>
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
  status: 'Unassigned',
  priority: 5,
  is_recurring: false,
  recurrence_interval: 'daily',
  recurrence_days: null,
  recurrence_end_date: null,
})

const handleSubmit = () => {
  if (!localData.value.title.trim() || !localData.value.deadline || !localData.value.description.trim()) {
    alert('Please fill in Title, Deadline and Description.')
    return
  }
  emit('submit', { ...localData.value })
  // Reset form after submission
  localData.value = {
    title: '',
    deadline: '',
    description: '',
    status: 'Unassigned',
    priority: 5,
    is_recurring: false,
    recurrence_interval: 'daily',
    recurrence_days: null,
    recurrence_end_date: null,
  }
}
</script>