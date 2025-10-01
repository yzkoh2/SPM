<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link 
            :to="`/tasks/${taskId}/subtasks/${subtaskId}`" 
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Subtask Details
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">Edit Subtask</h1>
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

      <!-- Parent Task Info -->
      <div v-if="parentTask" class="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-900">Parent Task:</p>
            <h3 class="text-lg font-semibold text-blue-800">{{ parentTask.title }}</h3>
          </div>
          <router-link 
            :to="`/tasks/${taskId}`"
            class="text-blue-600 hover:text-blue-500 text-sm font-medium">
            View Parent Task →
          </router-link>
        </div>
      </div>

      <!-- Completed Subtask Warning -->
      <div v-if="subtask && subtask.status === 'Completed'" class="bg-yellow-50 border border-yellow-200 rounded-md p-6 mb-6">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-yellow-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-yellow-800">Completed Subtask</h3>
            <p class="text-sm text-yellow-700 mt-1">This subtask is marked as completed and cannot be edited.</p>
          </div>
        </div>
      </div>

      <!-- Edit Form -->
      <div v-if="subtask && !loading && subtask.status !== 'Completed'" class="bg-white rounded-lg shadow-md p-6">
        <form @submit.prevent="confirmUpdate" class="space-y-6">
          <!-- Subtask Title -->
          <div>
            <label for="title" class="block text-sm font-medium text-gray-700">Subtask Title *</label>
            <input 
              v-model="editedSubtask.title" 
              type="text" 
              id="title"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              placeholder="Enter subtask title"
            />
          </div>

          <!-- Subtask Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
            <textarea 
              v-model="editedSubtask.description" 
              id="description"
              rows="4"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              placeholder="Enter subtask description"
            ></textarea>
          </div>

          <!-- Deadline -->
          <div>
            <label for="deadline" class="block text-sm font-medium text-gray-700">Deadline</label>
            <input 
              v-model="editedSubtask.deadline" 
              type="datetime-local" 
              id="deadline"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
            />
          </div>

          <!-- Collaborators Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Collaborators</label>
            <p class="text-xs text-gray-500 mb-3">Manage collaborators for this subtask</p>
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
            <label class="block text-sm font-medium text-gray-700 mb-2">Transfer Ownership (Assign Subtask)</label>
            <p class="text-xs text-gray-500 mb-3">
              Assign this subtask to another user in your department with a lower role.
            </p>
            <div class="flex items-center space-x-4">
              <select 
                v-model="transferToUserId"
                class="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              >
                <option value="">Select user to assign to</option>
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
                Assign Subtask
              </button>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex justify-end space-x-3 pt-6 border-t">
            <router-link 
              :to="`/tasks/${taskId}/subtasks/${subtaskId}`"
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </router-link>
            <button 
              type="submit"
              :disabled="saving"
              class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Update Subtask' }}
            </button>
          </div>
        </form>
      </div>
    </div>

      <!-- Confirmation Modal -->
      <div
        v-if="showConfirmModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
        @click.self="showConfirmModal = false"
      >
        <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
          <!-- Close (optional) -->
          <button
            @click="showConfirmModal = false"
            class="absolute top-3 right-3 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>

          <!-- Icon -->
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-indigo-100 mb-4">
            <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>

          <!-- Title & Message -->
          <h3 class="text-lg font-medium text-gray-900 text-center" id="modal-title">
            Confirm Update
          </h3>
          <p class="text-sm text-gray-500 mt-2 text-center">
            Are you sure you want to update this subtask? This will update it for all collaborators in real-time.
          </p>

          <!-- Buttons -->
          <div class="mt-6 flex space-x-3">
            <button
              @click="saveSubtask"
              class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Confirm
            </button>
            <button
              @click="showConfirmModal = false"
              class="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
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
const subtaskId = ref(route.params.subtaskId)
const subtask = ref(null)
const editedSubtask = ref({})
const parentTask = ref(null)
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
  await fetchSubtaskDetails()
  await fetchCollaborators()
  if (userRole.value !== 'staff') {
    await fetchAvailableUsers()
  }
})

// Fetch subtask details
const fetchSubtaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/subtasks/${subtaskId.value}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      subtask.value = await response.json()
      
      // Store parent task info
      if (subtask.value.parent_task) {
        parentTask.value = subtask.value.parent_task
      }
      
      // Initialize editedSubtask with current values
      editedSubtask.value = {
        title: subtask.value.title,
        description: subtask.value.description || '',
        deadline: subtask.value.deadline ? formatDateForInput(subtask.value.deadline) : ''
      }
      
      console.log('Subtask loaded:', subtask.value)
    } else if (response.status === 404) {
      error.value = 'Subtask not found'
    } else {
      error.value = `Failed to load subtask: ${response.status}`
    }
  } catch (err) {
    console.error('Error fetching subtask:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

// Fetch collaborators
const fetchCollaborators = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/subtasks/${subtaskId.value}/collaborators`, {
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

// Save subtask
const saveSubtask = async () => {
  try {
    saving.value = true
    showConfirmModal.value = false
    
    const updateData = {
      title: editedSubtask.value.title,
      description: editedSubtask.value.description,
      deadline: editedSubtask.value.deadline || null,
      requesting_user_id: userId.value
    }
    
    console.log('Sending subtask update request:', updateData)
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/subtasks/${subtaskId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    })
    
    const responseData = await response.json()
    console.log('Response:', responseData)
    
    if (response.ok) {
      alert('Subtask updated successfully!')
      router.push(`/tasks/${taskId.value}/subtasks/${subtaskId.value}`)
    } else {
      error.value = responseData.error || 'Failed to update subtask'
    }
  } catch (err) {
    console.error('Error updating subtask:', err)
    error.value = 'Failed to save changes: ' + err.message
  } finally {
    saving.value = false
  }
}

// Add collaborator
const addCollaborator = async () => {
  if (!newCollaboratorId.value) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/subtasks/${subtaskId.value}/collaborators`, {
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
      `${KONG_API_URL}/tasks/${taskId.value}/subtasks/${subtaskId.value}/collaborators/${collaboratorId}?requesting_user_id=${userId.value}`,
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

// Transfer ownership (assign subtask)
const transferOwnership = async () => {
  if (!transferToUserId.value) return
  
  const selectedUser = availableUsers.value.find(u => u.id === parseInt(transferToUserId.value))
  if (!selectedUser) return
  
  if (!confirm(`Assign subtask to ${selectedUser.name}?`)) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/subtasks/${subtaskId.value}/transfer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        requesting_user_id: userId.value,
        requesting_user_role: userRole.value,
        requesting_user_department: userDepartment.value,
        new_assignee_id: selectedUser.id,
        new_assignee_role: selectedUser.role,
        new_assignee_department: selectedUser.department
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      alert('Subtask assigned successfully!')
      await fetchSubtaskDetails()
      transferToUserId.value = ''
    } else {
      alert('Failed to assign subtask: ' + (data.error || 'Unknown error'))
    }
  } catch (err) {
    console.error('Error assigning subtask:', err)
    alert('Failed to assign subtask: ' + err.message)
  }
}
</script>