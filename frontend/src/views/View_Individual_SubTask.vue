<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with Back Navigation -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link 
            :to="`/tasks/${route.params.id}/subtasks`" 
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-4 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Subtasks
          </router-link>
          <router-link 
            :to="`/tasks/${route.params.id}`" 
            class="flex items-center text-gray-600 hover:text-gray-500 mr-6 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m8 7 4-4 4 4"></path>
            </svg>
            Parent Task
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">Subtask Details</h1>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-6">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error Loading Subtask</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
        <div class="mt-4">
          <button @click="fetchSubtaskDetails" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm">
            Try Again
          </button>
        </div>
      </div>
      
      <!-- Subtask Details -->
      <div v-else-if="subtask" class="space-y-6">
        <!-- Parent Task Reference -->
        <div v-if="parentTask" class="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-900">Part of:</p>
              <h3 class="text-lg font-semibold text-blue-800">{{ parentTask.title }}</h3>
            </div>
            <router-link 
              :to="`/tasks/${route.params.id}`"
              class="text-blue-600 hover:text-blue-500 text-sm font-medium">
              View Parent Task →
            </router-link>
          </div>
        </div>

        <!-- Subtask Header Card -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4" :class="getStatusBorderColor(subtask.status)">
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <h2 class="text-3xl font-bold text-gray-900 mb-2">{{ subtask.title }}</h2>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getStatusBadgeColor(subtask.status)">
                {{ subtask.status }}
              </span>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button @click="editSubtask" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Edit Subtask
              </button>
              <button @click="deleteSubtask" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Delete Subtask
              </button>
            </div>
          </div>
          
          <!-- Subtask Description -->
          <div class="mt-4">
            <h3 class="text-lg font-medium text-gray-900 mb-2">Description</h3>
            <p class="text-gray-700 leading-relaxed">
              {{ subtask.description || 'No description provided' }}
            </p>
          </div>
          
          <!-- Subtask Metadata -->
          <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-gray-200">
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Deadline</h4>
              <p class="mt-1 text-lg" :class="getDeadlineColor(subtask.deadline)">
                {{ formatDeadline(subtask.deadline) }}
              </p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Assignee</h4>
              <p class="mt-1 text-lg text-gray-900">{{ subtask.assignee_id || 'Unassigned' }}</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Created</h4>
              <p class="mt-1 text-lg text-gray-900">{{ formatDate(subtask.created_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Quick Status Update -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div class="flex items-center space-x-4">
            <label class="text-sm font-medium text-gray-700">Update Status:</label>
            <select 
              :value="subtask.status"
              @change="updateSubtaskStatus($event.target.value)"
              class="border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
              <option value="Completed">Completed</option>
              <option value="On Hold">On Hold</option>
            </select>
            <div v-if="statusUpdateLoading" class="flex items-center text-sm text-gray-500">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
              Updating...
            </div>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">Comments ({{ subtask.comments?.length || 0 }})</h3>
          
          <div v-if="subtask.comments && subtask.comments.length > 0" class="space-y-4">
            <div v-for="comment in subtask.comments" :key="comment.id" 
                 class="border-l-4 border-indigo-200 pl-4 py-2">
              <p class="text-gray-700">{{ comment.body }}</p>
              <p class="text-xs text-gray-500 mt-1">Author ID: {{ comment.author_id }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(comment.created_at) }}</p>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
            <p>No comments yet</p>
          </div>
        </div>

        <!-- Attachments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">Attachments ({{ subtask.attachments?.length || 0 }})</h3>
          
          <div v-if="subtask.attachments && subtask.attachments.length > 0" class="space-y-3">
            <div v-for="attachment in subtask.attachments" :key="attachment.id" 
                 class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                </svg>
                <span class="text-gray-900">{{ attachment.filename }}</span>
              </div>
              <a :href="attachment.url" target="_blank" 
                 class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                Download
              </a>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
            </svg>
            <p>No attachments</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// Reactive data
const subtask = ref(null)
const parentTask = ref(null)
const loading = ref(true)
const error = ref(null)
const statusUpdateLoading = ref(false)

// API configuration
const KONG_API_URL = "http://localhost:8000"

// Fetch subtask details from API
const fetchSubtaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const taskId = route.params.id
    const subtaskId = route.params.subtaskId
    console.log('Fetching subtask details for Task ID:', taskId, 'Subtask ID:', subtaskId)
    
    // Fetch subtask details
    const subtaskResponse = await fetch(`${KONG_API_URL}/tasks/${taskId}/subtasks/${subtaskId}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (subtaskResponse.ok) {
      subtask.value = await subtaskResponse.json()
      console.log('Subtask details loaded:', subtask.value)
    } else if (subtaskResponse.status === 404) {
      error.value = 'Subtask not found'
      return
    } else {
      error.value = `Failed to load subtask: ${subtaskResponse.status}`
      return
    }

    // Fetch parent task details
    const parentResponse = await fetch(`${KONG_API_URL}/tasks/${taskId}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (parentResponse.ok) {
      parentTask.value = await parentResponse.json()
      console.log('Parent task details loaded:', parentTask.value)
    } else {
      console.warn('Failed to load parent task details')
    }
    
  } catch (err) {
    console.error('Error fetching subtask details:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

// Update subtask status
const updateSubtaskStatus = async (newStatus) => {
  try {
    statusUpdateLoading.value = true
    
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks/${route.params.subtaskId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: newStatus
      })
    })
    
    if (response.ok) {
      subtask.value.status = newStatus
      console.log('Subtask status updated to:', newStatus)
    } else {
      throw new Error(`Failed to update status: ${response.status}`)
    }
  } catch (err) {
    console.error('Error updating subtask status:', err)
    alert('Failed to update subtask status: ' + err.message)
  } finally {
    statusUpdateLoading.value = false
  }
}

// Action methods
const editSubtask = () => {
  router.push(`/tasks/${route.params.id}/subtasks/${route.params.subtaskId}/edit`)
}

const deleteSubtask = async () => {
  if (!confirm('Are you sure you want to delete this subtask? This action cannot be undone.')) {
    return
  }
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks/${route.params.subtaskId}`, {
      method: 'DELETE'
    })
    
    if (response.ok || response.status === 404) {
      alert('Subtask deleted successfully!')
      router.push(`/tasks/${route.params.id}/subtasks`)
    } else {
      throw new Error(`Failed to delete: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting subtask:', err)
    alert('Failed to delete subtask: ' + err.message)
  }
}

// Utility methods
const getStatusBorderColor = (status) => {
  const colors = {
    'Unassigned': 'border-gray-400',
    'Ongoing': 'border-yellow-400',
    'Under Review': 'border-orange-400',
    'Completed': 'border-green-400',
    'On Hold': 'border-red-400'
  }
  return colors[status] || 'border-gray-400'
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

const getDeadlineColor = (deadline) => {
  if (!deadline) return 'text-gray-600'
  
  const now = new Date()
  const deadlineDate = new Date(deadline)
  
  if (deadlineDate < now) return 'text-red-600 font-medium'
  if (deadlineDate.toDateString() === now.toDateString()) return 'text-orange-600 font-medium'
  return 'text-gray-900'
}

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline set'
  const date = new Date(deadline)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not specified'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Load subtask details when component mounts
onMounted(() => {
  fetchSubtaskDetails()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>