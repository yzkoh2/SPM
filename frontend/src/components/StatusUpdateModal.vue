<template>
  <div v-if="show" class="fixed inset-0 z-[9999]" style="background-color: rgba(0,0,0,0.5);">
    <div class="flex items-center justify-center min-h-screen p-4">
      
      <!-- Modal Box -->
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-md p-6" style="position: relative; z-index: 10000;">
        
        <!-- Header -->
        <div class="mb-4">
          <h2 class="text-xl font-bold text-gray-900">Update Task Status</h2>
          <p class="text-sm text-gray-600 mt-1">Task: {{ task?.title || 'Unknown' }}</p>
        </div>

        <!-- Current Status Display -->
        <div class="mb-4 p-3 bg-gray-100 rounded">
          <p class="text-sm font-medium text-gray-700">Current Status:</p>
          <p class="text-lg font-semibold text-indigo-600">{{ currentStatus }}</p>
        </div>

        <!-- Status Dropdown -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            New Status:
          </label>
          <select 
            v-model="selectedStatus"
            class="w-full px-3 py-2 border-2 border-gray-300 rounded-md text-base"
            style="appearance: menulist;"
          >
            <option value="Unassigned">Unassigned</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Under Review">Under Review</option>
            <option value="Completed">Completed</option>
          </select>
        </div>

        <!-- Status Preview -->
        <div class="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
          <p class="text-sm text-gray-600">Change: 
            <span class="font-semibold">{{ currentStatus }}</span> 
            → 
            <span class="font-semibold text-blue-600">{{ selectedStatus }}</span>
          </p>
        </div>

        <!-- Comment -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Comment (Optional):
          </label>
          <textarea 
            v-model="comment"
            rows="3"
            class="w-full px-3 py-2 border-2 border-gray-300 rounded-md"
            placeholder="Add a comment..."
          ></textarea>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <!-- Buttons -->
        <div class="flex gap-3">
          <button 
            @click="confirmUpdate"
            :disabled="updating || selectedStatus === currentStatus"
            class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            style="min-height: 40px;"
          >
            {{ updating ? 'Updating...' : 'Confirm Update' }}
          </button>
          <button 
            @click="closeModal"
            :disabled="updating"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md font-medium hover:bg-gray-300 disabled:opacity-50"
            style="min-height: 40px;"
          >
            Cancel
          </button>
        </div>

        <!-- Debug Info -->
        <div class="mt-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
          <p><strong>Debug:</strong></p>
          <p>Show: {{ show }}</p>
          <p>Task ID: {{ task?.id }}</p>
          <p>Current: {{ currentStatus }}</p>
          <p>Selected: {{ selectedStatus }}</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  task: {
    type: Object,
    required: true,
    default: () => ({})
  },
  isSubtask: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'update-status'])

const currentStatus = computed(() => props.task?.status || 'Unassigned')
const selectedStatus = ref(currentStatus.value)
const comment = ref('')
const updating = ref(false)
const error = ref(null)

onMounted(() => {
  console.log('StatusUpdateModal mounted')
  console.log('Initial task:', props.task)
  console.log('Initial show:', props.show)
})

watch(() => props.task?.status, (newStatus) => {
  console.log('Task status changed to:', newStatus)
  if (newStatus) {
    selectedStatus.value = newStatus
  }
}, { immediate: true })

watch(() => props.show, (newVal) => {
  console.log('Modal show changed to:', newVal)
  if (newVal) {
    selectedStatus.value = currentStatus.value
    comment.value = ''
    error.value = null
    updating.value = false
  }
})

const closeModal = () => {
  console.log('Close modal called')
  if (!updating.value) {
    emit('close')
  }
}

const confirmUpdate = async () => {
  console.log('Confirm update called')
  console.log('Selected status:', selectedStatus.value)
  console.log('Current status:', currentStatus.value)
  
  if (selectedStatus.value === currentStatus.value) {
    console.log('No change detected')
    return
  }

  updating.value = true
  error.value = null

  try {
    console.log('Emitting update-status event')
    await emit('update-status', {
      newStatus: selectedStatus.value,
      comment: comment.value
    })
  } catch (err) {
    console.error('Error in confirmUpdate:', err)
    error.value = err.message || 'Failed to update status'
    updating.value = false
  }
}
</script>