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
          <!-- Attachments Section -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-2">Attachments</label>
  <p class="text-xs text-gray-500 mb-3">Upload files (images, PDFs, documents, etc.)</p>
  
  <!-- Existing Attachments -->
  <div v-if="task.attachments && task.attachments.length > 0" class="space-y-2 mb-4">
    <div v-for="attachment in task.attachments" :key="attachment.id" 
         class="flex items-center justify-between p-3 bg-gray-50 rounded-md border border-gray-200">
      <div class="flex items-center space-x-3">
        <!-- File Icon based on type -->
        <svg v-if="isImageFile(attachment.filename)" class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
        <svg v-else-if="isPdfFile(attachment.filename)" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
        </svg>
        <svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
        </svg>
        <div>
          <span class="text-sm text-gray-900 font-medium">{{ attachment.filename }}</span>
          <p class="text-xs text-gray-500">{{ getFileSize(attachment) }}</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <a :href="attachment.url" target="_blank" 
           class="text-indigo-600 hover:text-indigo-500 text-sm font-medium flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
          Download
        </a>
        <button 
          type="button"
          @click="deleteAttachment(attachment.id)"
          class="text-red-600 hover:text-red-500 text-sm font-medium flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
          </svg>
          Delete
        </button>
      </div>
    </div>
  </div>
  
        <!-- File Upload Area -->
        <div class="mt-4">
          <div class="flex items-center justify-center w-full">
            <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <svg class="w-8 h-8 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                <p class="mb-2 text-sm text-gray-500">
                  <span class="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p class="text-xs text-gray-500">PNG, JPG, PDF, DOC (MAX. 16MB)</p>
              </div>
              <input 
                type="file" 
                ref="fileInput"
                @change="handleFileSelect"
                class="hidden" 
                accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip,.rar"
              />
            </label>
          </div>
          
          <!-- Selected File Preview -->
          <div v-if="selectedFile" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <div>
                <p class="text-sm font-medium text-blue-900">{{ selectedFile.name }}</p>
                <p class="text-xs text-blue-700">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button 
                type="button"
                @click="uploadFile"
                :disabled="uploading"
                class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md disabled:opacity-50 flex items-center">
                <svg v-if="!uploading" class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-1"></div>
                {{ uploading ? 'Uploading...' : 'Upload' }}
              </button>
              <button 
                type="button"
                @click="clearSelectedFile"
                class="text-gray-600 hover:text-gray-800">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
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
              type="button"
              :disabled="saving"
              @click="confirmUpdate"
              class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-md disabled:opacity-50"
            >
              {{ saving ? 'Saving...' : 'Update Task' }}
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
      >
        <div
          class="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative"
        >
          <!-- Close on background click -->
          <button
            @click="showConfirmModal = false"
            class="absolute top-3 right-3 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>

          <!-- Icon -->
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-indigo-100 mb-4">
            <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>

          <!-- Title & Message -->
          <h3 class="text-lg font-medium text-gray-900 text-center" id="modal-title">
            Confirm Update
          </h3>
          <p class="text-sm text-gray-500 mt-2 text-center">
            Are you sure you want to update this task? This will update the task for all collaborators in real-time.
          </p>

          <!-- Buttons -->
          <div class="mt-6 flex space-x-3">
            <button
              @click="saveTask"
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


// Add to reactive data
const selectedFile = ref(null)
const uploading = ref(false)
const fileInput = ref(null)

// Helper functions
const isImageFile = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
}

const isPdfFile = (filename) => {
  return filename.toLowerCase().endsWith('.pdf')
}

const getFileSize = (attachment) => {
  // You can store file size in database if needed
  return 'Unknown size'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Check file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
      alert('File size exceeds 16MB limit')
      return
    }
    selectedFile.value = file
  }
}

const clearSelectedFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    alert('Please select a file first')
    return
  }

  try {
    uploading.value = true
    
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('requesting_user_id', userId.value)

    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}/attachments`, {
      method: 'POST',
      body: formData
      // Don't set Content-Type header - browser will set it with boundary for FormData
    })

    if (response.ok) {
      const attachment = await response.json()
      console.log('File uploaded successfully:', attachment)
      
      // Refresh task details to get updated attachments
      await fetchTaskDetails()
      
      // Clear selected file
      clearSelectedFile()
      
      alert('File uploaded successfully!')
    } else {
      const data = await response.json()
      throw new Error(data.error || 'Failed to upload file')
    }
  } catch (err) {
    console.error('Error uploading file:', err)
    alert('Failed to upload file: ' + err.message)
  } finally {
    uploading.value = false
  }
}

const deleteAttachment = async (attachmentId) => {
  if (!confirm('Are you sure you want to delete this attachment?')) {
    return
  }

  try {
    const response = await fetch(
      `${KONG_API_URL}/tasks/${taskId.value}/attachments/${attachmentId}?requesting_user_id=${userId.value}`,
      {
        method: 'DELETE'
      }
    )

    if (response.ok) {
      // Refresh task details to get updated attachments
      await fetchTaskDetails()
      console.log('Attachment deleted successfully')
      alert('Attachment deleted successfully!')
    } else {
      const data = await response.json()
      throw new Error(data.error || 'Failed to delete attachment')
    }
  } catch (err) {
    console.error('Error deleting attachment:', err)
    alert('Failed to delete attachment: ' + err.message)
  }
}
</script>