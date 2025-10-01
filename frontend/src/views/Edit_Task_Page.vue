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

      <!-- Edit Form -->
      <div v-if="task && !loading" class="bg-white rounded-lg shadow-md p-6">
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

          <!-- Status -->
          <div>
            <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
            <select 
              v-model="editedTask.status" 
              id="status"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              :disabled="originalTask.status === 'Completed'"
            >
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
              <option value="Completed">Completed</option>
            </select>
            <p v-if="originalTask.status === 'Completed'" class="mt-1 text-sm text-red-600">
              Completed tasks cannot be edited
            </p>
          </div>

          <!-- Collaborators Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Collaborators</label>
            <div class="space-y-2">
              <!-- List existing collaborators -->
              <div v-for="collaborator in collaborators" :key="collaborator.id" 
                   class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <span class="text-sm text-gray-900">{{ collaborator.name }} (ID: {{ collaborator.id }})</span>
                <button 
                  type="button"
                  @click="removeCollaborator(collaborator.id)"
                  class="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
              
              <!-- Add new collaborator -->
              <div class="flex items-center space-x-2 mt-3">
                <input 
                  v-model="newCollaboratorId" 
                  type="number" 
                  placeholder="User ID"
                  class="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                />
                <button 
                  type="button"
                  @click="addCollaborator"
                  class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md"
                >
                  Add Collaborator
                </button>
              </div>
            </div>
          </div>

          <!-- Attachments Section -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Attachments</label>
            <div class="space-y-2">
              <!-- List existing attachments -->
              <div v-for="attachment in editedTask.attachments" :key="attachment.id" 
                   class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div class="flex items-center space-x-2">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                  </svg>
                  <span class="text-sm text-gray-900">{{ attachment.filename }}</span>
                </div>
                <button 
                  type="button"
                  @click="removeAttachment(attachment.id)"
                  class="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
              
              <!-- Add new attachment -->
              <div class="mt-3 p-3 border-2 border-dashed border-gray-300 rounded-md">
                <input 
                  type="file" 
                  @change="handleFileUpload"
                  class="w-full text-sm text-gray-500"
                />
              </div>
            </div>
          </div>

          <!-- Assign Task (for Managers/Directors only) -->
          <div v-if="userRole === 'manager' || userRole === 'director'" class="border-t pt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Assign Task</h3>
            <div class="flex items-center space-x-4">
              <select 
                v-model="assignToUserId"
                class="flex-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
              >
                <option value="">Select user to assign</option>
                <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                  {{ user.name }} ({{ user.role }})
                </option>
              </select>
              <button 
                type="button"
                @click="assignTask"
                :disabled="!assignToUserId"
                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
              >
                Assign Task
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
              :disabled="saving || originalTask.status === 'Completed'"
              class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="fixed z-50 inset-0 overflow-y-auto">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 sm:mx-0 sm:h-10 sm:w-10">
              <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="text-lg leading-6 font-medium text-gray-900">Confirm Changes</h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Are you sure you want to save these changes? This will update the task for all collaborators.
                </p>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button 
              @click="saveTask"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Confirm
            </button>
            <button 
              @click="showConfirmModal = false"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
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

// Reactive data
const taskId = ref(route.params.id)
const task = ref(null)
const originalTask = ref(null)
const editedTask = ref({})
const collaborators = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const showConfirmModal = ref(false)
const newCollaboratorId = ref('')
const assignToUserId = ref('')
const availableUsers = ref([])

// User role and permissions
const userRole = ref(authStore.user?.role || 'staff')
const userId = ref(authStore.user?.id)
const userDepartment = ref(authStore.user?.department || 'engineering') // You'll need to add this to auth store

// API configuration
const KONG_API_URL = "http://localhost:8000"

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
      originalTask.value = JSON.parse(JSON.stringify(task.value))
      editedTask.value = JSON.parse(JSON.stringify(task.value))
      
      // Convert deadline to datetime-local format
      if (editedTask.value.deadline) {
        const date = new Date(editedTask.value.deadline)
        editedTask.value.deadline = date.toISOString().slice(0, 16)
      }
      
      // Check ownership
      if (task.value.owner_id !== userId.value) {
        error.value = 'You are not authorized to edit this task'
        router.push(`/tasks/${taskId.value}`)
      }
      
      // Check if completed
      if (task.value.status === 'Completed') {
        error.value = 'Completed tasks cannot be edited'
      }
      
      // Fetch collaborators if any
      // This would be a separate API call in production
      collaborators.value = []
      
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

// Fetch available users for assignment
const fetchAvailableUsers = async () => {
  // This would be an API call to get users in the same department with lower roles
  // For now, using mock data
  if (userRole.value === 'director') {
    availableUsers.value = [
      { id: 2, name: 'John Manager', role: 'manager' },
      { id: 3, name: 'Jane Staff', role: 'staff' }
    ]
  } else if (userRole.value === 'manager') {
    availableUsers.value = [
      { id: 3, name: 'Jane Staff', role: 'staff' },
      { id: 4, name: 'Bob Staff', role: 'staff' }
    ]
  }
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
      ...editedTask.value,
      requesting_user_id: userId.value
    }
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    })
    
    if (response.ok) {
      router.push(`/tasks/${taskId.value}`)
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Failed to update task'
    }
  } catch (err) {
    console.error('Error updating task:', err)
    error.value = 'Failed to save changes'
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
      collaborators.value.push({
        id: parseInt(newCollaboratorId.value),
        name: `User ${newCollaboratorId.value}`
      })
      newCollaboratorId.value = ''
    } else {
      const errorData = await response.json()
      alert(errorData.error || 'Failed to add collaborator')
    }
  } catch (err) {
    console.error('Error adding collaborator:', err)
    alert('Failed to add collaborator')
  }
}

// Remove collaborator
const removeCollaborator = async (collaboratorId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/collaborators/${collaboratorId}?requesting_user_id=${userId.value}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      collaborators.value = collaborators.value.filter(c => c.id !== collaboratorId)
    } else {
      const errorData = await response.json()
      alert(errorData.error || 'Failed to remove collaborator')
    }
  } catch (err) {
    console.error('Error removing collaborator:', err)
    alert('Failed to remove collaborator')
  }
}

// Handle file upload
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // In production, you'd upload the file to a storage service
    // For now, just add to the attachments list
    const newAttachment = {
      id: Date.now(),
      filename: file.name,
      url: URL.createObjectURL(file)
    }
    
    if (!editedTask.value.attachments) {
      editedTask.value.attachments = []
    }
    editedTask.value.attachments.push(newAttachment)
  }
}

// Remove attachment
const removeAttachment = (attachmentId) => {
  editedTask.value.attachments = editedTask.value.attachments.filter(a => a.id !== attachmentId)
}

// Assign task
const assignTask = async () => {
  if (!assignToUserId.value) return
  
  try {
    const selectedUser = availableUsers.value.find(u => u.id === parseInt(assignToUserId.value))
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/assign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        requesting_user_id: userId.value,
        requesting_user_role: userRole.value,
        requesting_user_department: userDepartment.value,
        new_owner_id: parseInt(assignToUserId.value),
        new_owner_role: selectedUser.role,
        new_owner_department: userDepartment.value // Same department requirement
      })
    })
    
    if (response.ok) {
      alert('Task assigned successfully!')
      router.push(`/tasks/${taskId.value}`)
    } else {
      const errorData = await response.json()
      alert(errorData.error || 'Failed to assign task')
    }
  } catch (err) {
    console.error('Error assigning task:', err)
    alert('Failed to assign task')
  }
}

// Load data on mount
onMounted(() => {
  fetchTaskDetails()
  fetchAvailableUsers()
})
</script>

<style scoped>
/* Add any custom styles here */
</style>