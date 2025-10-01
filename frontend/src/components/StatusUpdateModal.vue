<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeModal"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <!-- Icon -->
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10"
                 :class="getIconColor()">
              <svg class="h-6 w-6" :class="getIconTextColor()" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            
            <!-- Content -->
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left flex-1">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                {{ isSubtask ? 'Update Subtask Status' : 'Update Task Status' }}
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Update the status of <strong>"{{ task.title }}"</strong>
                </p>
              </div>

              <!-- Status Selection -->
              <div class="mt-4">
                <label for="status" class="block text-sm font-medium text-gray-700">
                  Select New Status
                </label>
                <select 
                  id="status"
                  v-model="selectedStatus" 
                  class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                  <option value="Unassigned">Unassigned</option>
                  <option value="Ongoing">Ongoing</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Completed">Completed</option>
                  <option v-if="isSubtask" value="On Hold">On Hold</option>
                </select>
                
                <!-- Status change indicator -->
                <div class="mt-2 text-sm text-gray-600">
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                        :class="getStatusBadgeColor(task.status)">
                    {{ task.status }}
                  </span>
                  <svg class="inline-block mx-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                  </svg>
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                        :class="getStatusBadgeColor(selectedStatus)">
                    {{ selectedStatus }}
                  </span>
                </div>
              </div>

              <!-- Warning for completion -->
              <div v-if="!isSubtask && selectedStatus === 'Completed' && task.subtask_count > 0" 
                   class="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <div class="flex">
                  <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                  </svg>
                  <div class="ml-3">
                    <p class="text-sm text-yellow-700">
                      This task has {{ task.subtask_count }} subtask(s). All subtasks must be completed before marking this task as completed.
                    </p>
                  </div>
                </div>
              </div>

              <!-- Comment Section -->
              <div class="mt-4">
                <label for="comment" class="block text-sm font-medium text-gray-700">
                  Add Comment (Optional)
                </label>
                <p class="text-xs text-gray-500 mb-2">Explain the reason for this status change</p>
                <textarea 
                  id="comment"
                  v-model="comment"
                  rows="3"
                  class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  placeholder="e.g., Completed all requirements and passed testing..."
                ></textarea>
              </div>

              <!-- Error Message -->
              <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-md p-3">
                <div class="flex">
                  <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                  </svg>
                  <div class="ml-3">
                    <p class="text-sm text-red-700">{{ error }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button"
            @click="confirmUpdate"
            :disabled="updating || selectedStatus === task.status"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="updating" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Updating...
            </span>
            <span v-else>Confirm Update</span>
          </button>
          <button 
            type="button"
            @click="closeModal"
            :disabled="updating"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  task: {
    type: Object,
    required: true
  },
  isSubtask: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'update-status'])

const selectedStatus = ref(props.task.status)
const comment = ref('')
const updating = ref(false)
const error = ref(null)

// Watch for task changes to update selected status
watch(() => props.task.status, (newStatus) => {
  selectedStatus.value = newStatus
})

const closeModal = () => {
  if (!updating.value) {
    selectedStatus.value = props.task.status
    comment.value = ''
    error.value = null
    emit('close')
  }
}

const confirmUpdate = async () => {
  if (selectedStatus.value === props.task.status) {
    return
  }

  updating.value = true
  error.value = null

  try {
    await emit('update-status', {
      newStatus: selectedStatus.value,
      comment: comment.value
    })
    
    // Success - close modal
    comment.value = ''
    emit('close')
  } catch (err) {
    error.value = err.message || 'Failed to update status'
  } finally {
    updating.value = false
  }
}

const getIconColor = () => {
  const colors = {
    'Unassigned': 'bg-gray-100',
    'Ongoing': 'bg-yellow-100',
    'Under Review': 'bg-orange-100',
    'Completed': 'bg-green-100',
    'On Hold': 'bg-red-100'
  }
  return colors[selectedStatus.value] || 'bg-gray-100'
}

const getIconTextColor = () => {
  const colors = {
    'Unassigned': 'text-gray-600',
    'Ongoing': 'text-yellow-600',
    'Under Review': 'text-orange-600',
    'Completed': 'text-green-600',
    'On Hold': 'text-red-600'
  }
  return colors[selectedStatus.value] || 'text-gray-600'
}

const getStatusBadgeColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    'Completed': 'bg-green-100 text-green-800',
    'On Hold': 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}
</script>