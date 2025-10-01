<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link 
            :to="`/tasks/${taskId}`" 
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Task Details
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">Edit Task</h1>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Completed Task Warning -->
      <div v-if="task && task.status === 'Completed'" class="bg-yellow-50 border border-yellow-200 rounded-md p-6 mb-6">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-yellow-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-yellow-800">Completed Task</h3>
            <p class="text-sm text-yellow-700 mt-1">This task is marked as completed and cannot be edited.</p>
          </div>
        </div>
      </div>

      <!-- Edit Form -->
      <div v-if="task && !loading && task.status !== 'Completed'" class="bg-white rounded-lg shadow-md p-6">
        <form @submit.prevent="confirmUpdate" class="space-y-6">
          <!-- Task Title -->
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700">Task Title *</label>
            <input 
              v-model="editedTask.title" 
              type="text" 
              id="title"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              placeholder="Enter task title"
            />
          </div>

          <!-- Task Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea 
              v-model="editedTask.description" 
              id="description"
              rows="4"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              placeholder="Enter task description"
            ></textarea>
          </div>

          <!-- Deadline -->
          <div>
            <label for="deadline" class="block text-sm font-medium text-gray-700">Deadline</label>
            <input 
              v-model="editedTask.deadline" 
              type="datetime-local" 
              id="deadline"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
            />
          </div>

          <!-- Collaborators Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Collaborators</label>
            <div class="space-y-2">
              <!-- List existing collaborators -->
              <div v-for="collaborator in collaborators" :key="collaborator.user_id" 
                   class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <span class="text-sm text-gray-700">User ID: {{ collaborator.user_id }}</span>
                <button 
                  type="button"
                  @click="removeCollaborator(collaborator.user_id)"
                  class="text-red-600 hover:text-red-700 text-sm font-medium"
                >
                  Remove
                </button>
              </div>
              
              <!-- Add new collaborator -->
              <div class="flex items-center space-x-2 mt-3">
                <input 
                  v-model="newCollaboratorId"
                  type="number"
                  placeholder="Enter user ID"
                  class="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                />
                <button 
                  type="button"
                  @click="addCollaborator"
                  :disabled="!newCollaboratorId"
                  class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
                >
                  Add Collaborator
                </button>
              </div>
            </div>
          </div>

          <!-- Transfer Ownership Section -->
          <div v-if="userRole === 'manager' || userRole === 'director'" class="border-t pt-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Transfer Ownership</label>
            <p class="text-xs text-gray-500 mb-3">
              Transfer this task to another user in your department with a lower role.
            </p>
            <div class="flex items-center space-x-4">
              <select 
                v-model="transferToUserId"
                class="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              >
                <option value="">Select user to transfer to</option>
                <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                  {{ user.name }} ({{ user.role }})
                </option>
              </select>
              <button 
                type="button"
                @click="transferOwnership"
                :disabled="!transferToUserId"
                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
              >
                Transfer Task
              </button>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-6 border-t">
            <router-link 
              :to="`/tasks/${taskId}`"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </router-link>
            <button 
              type="submit"
              :disabled="saving"
              class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Update Task' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="fixed z-50 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showConfirmModal = false"></div>

        <!-- Center modal -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div>
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-indigo-100">
              <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-5">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">Confirm Update</h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Are you sure you want to update this task? 
                  This will update the task for all collaborators in real-time.
                </p>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button 
              @click="saveTask"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:col-start-2 sm:text-sm"
            >
              Confirm
            </button>
            <button 
              @click="showConfirmModal = false"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// API configuration
const KONG_API_URL = "http://localhost:8000"

// Reactive data
const taskId = ref(route.params.id)
const task = ref(null)
const editedTask = ref({})
const collaborators = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const showConfirmModal = ref(false)
const newCollaboratorId = ref('')
const transferToUserId = ref('')
const availableUsers = ref([])

// User role and permissions
const userRole = ref(authStore.user?.role || 'staff')
const userId = ref(authStore.user?.id)
const userDepartment = ref(authStore.user?.department)

// Lifecycle hooks
onMounted(async () => {
  await fetchTaskDetails()
  await fetchCollaborators()
  if (userRole.value !== 'staff') {
    await fetchAvailableUsers()
  }
})

// Fetch task details
const fetchTaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      task.value = await response.json()
      
      // Initialize editedTask with current values
      editedTask.value = {
        title: task.value.title,
        description: task.value.description || '',
        deadline: task.value.deadline ? formatDateForInput(task.value.deadline) : ''
      }
      
      console.log('Task loaded:', task.value)
    } else if (response.status === 404) {
      error.value = 'Task not found'
    } else {
      error.value = `Failed to load task: ${response.status}`
    }
  } catch (err) {
    console.error('Error fetching task:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

// Fetch collaborators
const fetchCollaborators = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/collaborators`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      collaborators.value = await response.json()
    }
  } catch (err) {
    console.error('Error fetching collaborators:', err)
  }
}

// Fetch available users for transfer (mock data - replace with actual API call)
const fetchAvailableUsers = async () => {
  // In production, fetch from user service based on department and role
  // For now, using mock data
  if (userRole.value === 'director') {
    availableUsers.value = [
      { id: 2, name: 'John Manager', role: 'manager', department: userDepartment.value },
      { id: 3, name: 'Jane Staff', role: 'staff', department: userDepartment.value }
    ]
  } else if (userRole.value === 'manager') {
    availableUsers.value = [
      { id: 3, name: 'Jane Staff', role: 'staff', department: userDepartment.value },
      { id: 4, name: 'Bob Staff', role: 'staff', department: userDepartment.value }
    ]
  }
}

// Format date for datetime-local input
const formatDateForInput = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// Confirm update
const confirmUpdate = () => {
  showConfirmModal.value = true
}

// Save task
const saveTask = async () => {
  try {
    saving.value = true
    showConfirmModal.value = false
    
    const updateData = {
      title: editedTask.value.title,
      description: editedTask.value.description,
      deadline: editedTask.value.deadline || null,
      requesting_user_id: userId.value
    }
    
    console.log('Sending update request:', updateData)
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    })
    
    const responseData = await response.json()
    console.log('Response:', responseData)
    
    if (response.ok) {
      alert('Task updated successfully!')
      router.push(`/tasks/${taskId.value}`)
    } else {
      error.value = responseData.error || 'Failed to update task'
    }
  } catch (err) {
    console.error('Error updating task:', err)
    error.value = 'Failed to save changes: ' + err.message
  } finally {
    saving.value = false
  }
}

// Add collaborator
const addCollaborator = async () => {
  if (!newCollaboratorId.value) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/collaborators`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        requesting_user_id: userId.value,
        collaborator_id: parseInt(newCollaboratorId.value)
      })
    })
    
    if (response.ok) {
      await fetchCollaborators()
      newCollaboratorId.value = ''
      alert('Collaborator added successfully!')
    } else {
      const data = await response.json()
      alert('Failed to add collaborator: ' + (data.error || 'Unknown error'))
    }
  } catch (err) {
    console.error('Error adding collaborator:', err)
    alert('Failed to add collaborator: ' + err.message)
  }
}

// Remove collaborator
const removeCollaborator = async (collaboratorId) => {
  if (!confirm('Are you sure you want to remove this collaborator?')) return
  
  try {
    const response = await fetch(
      `${KONG_API_URL}/tasks/${taskId.value}/collaborators/${collaboratorId}?requesting_user_id=${userId.value}`,
      { method: 'DELETE' }
    )
    
    if (response.ok) {
      await fetchCollaborators()
      alert('Collaborator removed successfully!')
    } else {
      const data = await response.json()
      alert('Failed to remove collaborator: ' + (data.error || 'Unknown error'))
    }
  } catch (err) {
    console.error('Error removing collaborator:', err)
    alert('Failed to remove collaborator: ' + err.message)
  }
}

// Transfer ownership
const transferOwnership = async () => {
  if (!transferToUserId.value) return
  
  const selectedUser = availableUsers.value.find(u => u.id === parseInt(transferToUserId.value))
  if (!selectedUser) return
  
  if (!confirm(`Transfer task ownership to ${selectedUser.name}?`)) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/transfer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        requesting_user_id: userId.value,
        requesting_user_role: userRole.value,
        requesting_user_department: userDepartment.value,
        new_owner_id: selectedUser.id,
        new_owner_role: selectedUser.role,
        new_owner_department: selectedUser.department
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      alert('Task ownership transferred successfully!')
      router.push('/tasks')
    } else {
      alert('Failed to transfer ownership: ' + (data.error || 'Unknown error'))
    }
  } catch (err) {
    console.error('Error transferring ownership:', err)
    alert('Failed to transfer ownership: ' + err.message)
  }
}
</script>