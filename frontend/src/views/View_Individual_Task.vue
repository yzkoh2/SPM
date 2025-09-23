<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with Back Navigation -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link 
            to="/tasks" 
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Tasks
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">Task Details</h1>
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
            <h3 class="text-sm font-medium text-red-800">Error Loading Task</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
        <div class="mt-4">
          <button @click="fetchTaskDetails" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm">
            Try Again
          </button>
        </div>
      </div>
      
      <!-- Task Details -->
      <div v-else-if="task" class="space-y-6">
        <!-- Task Header Card -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4" :class="getStatusBorderColor(task.status)">
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <h2 class="text-3xl font-bold text-gray-900 mb-2">{{ task.title }}</h2>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                    :class="getStatusBadgeColor(task.status)">
                {{ task.status }}
              </span>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button @click="editTask" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Edit Task
              </button>
              <button @click="deleteTask" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Delete Task
              </button>
            </div>
          </div>
          
          <!-- Task Description -->
          <div class="mt-4">
            <h3 class="text-lg font-medium text-gray-900 mb-2">Description</h3>
            <p class="text-gray-700 leading-relaxed">
              {{ task.description || 'No description provided' }}
            </p>
          </div>
          
          <!-- Task Metadata -->
          <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-gray-200">
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Deadline</h4>
              <p class="mt-1 text-lg" :class="getDeadlineColor(task.deadline)">
                {{ formatDeadline(task.deadline) }}
              </p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Owner</h4>
              <p class="mt-1 text-lg text-gray-900">ID: {{ task.owner_id }}</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Created</h4>
              <p class="mt-1 text-lg text-gray-900">{{ formatDate(task.deadline) }}</p>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Subtasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ task.subtasks?.length || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Comments</p>
                <p class="text-2xl font-semibold text-gray-900">{{ task.comments?.length || 0 }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-purple-100 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Attachments</p>
                <p class="text-2xl font-semibold text-gray-900">{{ task.attachments?.length || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Subtasks Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900">Subtasks ({{ task.subtasks?.length || 0 }})</h3>
            <router-link 
              :to="`/tasks/${task.id}/subtasks`"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              View All Subtasks
            </router-link>
          </div>
          
          <div v-if="task.subtasks && task.subtasks.length > 0" class="space-y-3">
            <div v-for="subtask in task.subtasks.slice(0, 5)" :key="subtask.id" 
                 class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <div class="w-2 h-2 rounded-full" :class="getSubtaskStatusColor(subtask.status)"></div>
                <span class="text-gray-900">{{ subtask.title }}</span>
              </div>
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                    :class="getStatusBadgeColor(subtask.status)">
                {{ subtask.status }}
              </span>
            </div>
            <div v-if="task.subtasks.length > 5" class="text-center pt-4">
              <router-link 
                :to="`/tasks/${task.id}/subtasks`"
                class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                View {{ task.subtasks.length - 5 }} more subtasks →
              </router-link>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <p>No subtasks yet</p>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">Comments ({{ task.comments?.length || 0 }})</h3>
          
          <div v-if="task.comments && task.comments.length > 0" class="space-y-4">
            <div v-for="comment in task.comments" :key="comment.id" 
                 class="border-l-4 border-indigo-200 pl-4 py-2">
              <p class="text-gray-700">{{ comment.body }}</p>
              <p class="text-xs text-gray-500 mt-1">Author ID: {{ comment.author_id }}</p>
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
          <h3 class="text-xl font-semibold text-gray-900 mb-6">Attachments ({{ task.attachments?.length || 0 }})</h3>
          
          <div v-if="task.attachments && task.attachments.length > 0" class="space-y-3">
            <div v-for="attachment in task.attachments" :key="attachment.id" 
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
const task = ref(null)
const loading = ref(true)
const error = ref(null)

// API configuration
const KONG_API_URL = "http://localhost:8000"

// Fetch task details from API
const fetchTaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const taskId = route.params.id
    console.log('Fetching task details for ID:', taskId)
    
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      task.value = await response.json()
      console.log('Task details loaded:', task.value)
    } else if (response.status === 404) {
      error.value = 'Task not found'
    } else {
      error.value = `Failed to load task: ${response.status}`
    }
  } catch (err) {
    console.error('Error fetching task details:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

// Action methods
const editTask = () => {
  console.log('Edit task:', task.value)
  // TODO: Implement edit functionality
  alert('Edit functionality coming soon!')
}

const deleteTask = async () => {
  if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
    return
  }
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok || response.status === 404) {
      alert('Task deleted successfully!')
      router.push('/tasks')
    } else {
      throw new Error(`Failed to delete: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting task:', err)
    alert('Failed to delete task: ' + err.message)
  }
}

// Utility methods
const getStatusBorderColor = (status) => {
  const colors = {
    'Unassigned': 'border-gray-400',
    'Ongoing': 'border-yellow-400',
    'Under Review': 'border-orange-400',
    'Completed': 'border-green-400'
  }
  return colors[status] || 'border-gray-400'
}

const getStatusBadgeColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    'Completed': 'bg-green-100 text-green-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getSubtaskStatusColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-400',
    'Ongoing': 'bg-yellow-400',
    'Under Review': 'bg-orange-400',
    'Completed': 'bg-green-400'
  }
  return colors[status] || 'bg-gray-400'
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
    day: 'numeric'
  })
}

// Load task details when component mounts
onMounted(() => {
  fetchTaskDetails()
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