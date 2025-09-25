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
                {{ formatStatus(task.status) }}
              </span>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button @click="showAssignmentDialog" 
                      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                {{ task.assigned_to ? 'Reassign' : 'Assign Task' }}
              </button>
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
          <div class="mt-6 grid grid-cols-1 md:grid-cols-4 gap-6 pt-6 border-t border-gray-200">
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Deadline</h4>
              <p class="mt-1 text-lg" :class="getDeadlineColor(task.deadline)">
                {{ formatDeadline(task.deadline) }}
              </p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Owner</h4>
              <p class="mt-1 text-lg text-gray-900">User {{ task.owner_id }}</p>
              <p class="text-xs text-gray-500">{{ task.owner_id === task.created_by ? 'Original Creator' : 'Transferred' }}</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Assigned To</h4>
              <p class="mt-1 text-lg text-gray-900">
                {{ task.assigned_to ? `User ${task.assigned_to}` : 'Unassigned' }}
              </p>
              <p v-if="task.is_unassigned" class="text-xs text-orange-600">Available for assignment</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Created</h4>
              <p class="mt-1 text-lg text-gray-900">{{ formatDate(task.created_at) }}</p>
              <p class="text-xs text-gray-500">by User {{ task.created_by }}</p>
            </div>
          </div>
        </div>

        <!-- Progress Overview -->
        <div v-if="task.subtask_count > 0" class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-4">Progress Overview</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center">
              <div class="text-3xl font-bold text-indigo-600">{{ task.completion_percentage || 0 }}%</div>
              <div class="text-sm text-gray-600">Complete</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-gray-900">{{ task.subtask_count }}</div>
              <div class="text-sm text-gray-600">Total Subtasks</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-green-600">
                {{ Object.values(task.subtask_status_summary || {}).reduce((a, b) => a + (b || 0), 0) }}
              </div>
              <div class="text-sm text-gray-600">Active Subtasks</div>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div class="mt-6">
            <div class="flex justify-between text-sm text-gray-600 mb-2">
              <span>Overall Progress</span>
              <span>{{ task.completion_percentage || 0 }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div 
                class="bg-green-600 h-3 rounded-full transition-all duration-500" 
                :style="{ width: (task.completion_percentage || 0) + '%' }"
              ></div>
            </div>
          </div>

          <!-- Status Summary -->
          <div v-if="task.subtask_status_summary" class="mt-6">
            <h4 class="text-sm font-medium text-gray-700 mb-3">Subtask Status Breakdown</h4>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="(count, status) in task.subtask_status_summary" 
                :key="status"
                class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                :class="getStatusBadgeColor(status)"
              >
                {{ count }} {{ formatStatus(status) }}
              </span>
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
            <div class="flex space-x-2">
              <button @click="showCreateSubtaskDialog = true"
                      class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Add Subtask
              </button>
              <router-link 
                :to="`/tasks/${task.id}/subtasks`"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Manage All Subtasks
              </router-link>
            </div>
          </div>
          
          <div v-if="task.subtasks && task.subtasks.length > 0" class="space-y-3">
            <div v-for="subtask in task.subtasks.slice(0, 5)" :key="subtask.id" 
                 class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 rounded-full" :class="getSubtaskStatusColor(subtask.status)"></div>
                <div class="flex-1">
                  <h4 class="text-sm font-medium text-gray-900"
                      :class="{ 'line-through text-gray-500': subtask.status === 'completed' }">
                    {{ subtask.title }}
                  </h4>
                  <p class="text-xs text-gray-500">
                    {{ subtask.assigned_to ? `Assigned to User ${subtask.assigned_to}` : 'Unassigned' }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                      :class="getStatusBadgeColor(subtask.status)">
                  {{ formatStatus(subtask.status) }}
                </span>
                <router-link 
                  :to="`/tasks/${task.id}/subtasks/${subtask.id}`"
                  class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                  View
                </router-link>
              </div>
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
            <p class="mb-4">No subtasks yet</p>
            <button @click="showCreateSubtaskDialog = true"
                    class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              Add First Subtask
            </button>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">Comments ({{ task.comments?.length || 0 }})</h3>
          
          <div v-if="task.comments && task.comments.length > 0" class="space-y-4">
            <div v-for="comment in task.comments" :key="comment.id" 
                 class="border-l-4 border-indigo-200 pl-4 py-2">
              <p class="text-gray-700">{{ comment.content }}</p>
              <p class="text-xs text-gray-500 mt-1">
                User {{ comment.created_by }} • {{ formatDate(comment.created_at) }}
              </p>
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
                <div>
                  <span class="text-gray-900">{{ attachment.file_name }}</span>
                  <p class="text-xs text-gray-500">
                    {{ formatFileSize(attachment.file_size) }} • {{ attachment.mime_type }}
                  </p>
                </div>
              </div>
              <a :href="attachment.file_path" target="_blank" 
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

      <!-- Assignment Dialog -->
      <div v-if="showAssignDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ task?.assigned_to ? 'Reassign Task' : 'Assign Task' }}
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            This will transfer ownership to the assignee.
          </p>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Assign to User ID:
              </label>
              <input 
                v-model="assignmentUserId" 
                type="number" 
                placeholder="Enter user ID"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button @click="showAssignDialog = false" 
                    class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
              Cancel
            </button>
            <button @click="assignTask" :disabled="!assignmentUserId"
                    class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
              Assign
            </button>
          </div>
        </div>
      </div>

      <!-- Create Subtask Dialog -->
      <div v-if="showCreateSubtaskDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Create New Subtask</h3>
          
          <form @submit.prevent="createSubtask" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
              <input 
                v-model="newSubtask.title" 
                type="text" 
                required
                placeholder="Enter subtask title"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea 
                v-model="newSubtask.description" 
                rows="3"
                placeholder="Enter subtask description (optional)"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Assign to (Optional)</label>
              <input 
                v-model="newSubtask.assigned_to" 
                type="number" 
                placeholder="User ID"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
            
            <div class="flex justify-end space-x-3">
              <button type="button" @click="cancelCreateSubtask" 
                      class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
                Cancel
              </button>
              <button type="submit" :disabled="!newSubtask.title"
                      class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
                Create Subtask
              </button>
            </div>
          </form>
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
const showAssignDialog = ref(false)
const showCreateSubtaskDialog = ref(false)
const assignmentUserId = ref('')

// New subtask form
const newSubtask = ref({
  title: '',
  description: '',
  assigned_to: null
})

// API configuration
const KONG_API_URL = "http://localhost:8000"
const currentUserId = 1

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

// Assignment methods
const showAssignmentDialog = () => {
  assignmentUserId.value = task.value.assigned_to || ''
  showAssignDialog.value = true
}

const assignTask = async () => {
  if (!assignmentUserId.value) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}/assign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        assigned_to: parseInt(assignmentUserId.value),
        updated_by: currentUserId
      })
    })
    
    if (response.ok) {
      await fetchTaskDetails()
      showAssignDialog.value = false
      assignmentUserId.value = ''
      alert('Task assigned successfully!')
    } else {
      throw new Error(`Failed to assign task: ${response.status}`)
    }
  } catch (err) {
    console.error('Error assigning task:', err)
    alert('Failed to assign task: ' + err.message)
  }
}

// Subtask methods
const createSubtask = async () => {
  if (!newSubtask.value.title) return
  
  try {
    const subtaskData = {
      title: newSubtask.value.title,
      description: newSubtask.value.description || null,
      created_by: currentUserId,
      assigned_to: newSubtask.value.assigned_to || null
    }
    
    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}/subtasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(subtaskData)
    })
    
    if (response.ok) {
      await fetchTaskDetails()
      cancelCreateSubtask()
      alert('Subtask created successfully!')
    } else {
      throw new Error(`Failed to create subtask: ${response.status}`)
    }
  } catch (err) {
    console.error('Error creating subtask:', err)
    alert('Failed to create subtask: ' + err.message)
  }
}

const cancelCreateSubtask = () => {
  showCreateSubtaskDialog.value = false
  newSubtask.value = {
    title: '',
    description: '',
    assigned_to: null
  }
}

// Action methods
const editTask = () => {
  console.log('Edit task:', task.value)
  alert('Edit functionality coming soon!')
}

const deleteTask = async () => {
  if (!confirm('Are you sure you want to delete this task? This will also delete all subtasks.')) {
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
    'unassigned': 'border-gray-400',
    'ongoing': 'border-yellow-400',
    'under_review': 'border-orange-400',
    'completed': 'border-green-400'
  }
  return colors[status] || 'border-gray-400'
}

const getStatusBadgeColor = (status) => {
  const colors = {
    'unassigned': 'bg-gray-100 text-gray-800',
    'ongoing': 'bg-yellow-100 text-yellow-800',
    'under_review': 'bg-orange-100 text-orange-800',
    'completed': 'bg-green-100 text-green-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getSubtaskStatusColor = (status) => {
  const colors = {
    'unassigned': 'bg-gray-400',
    'ongoing': 'bg-yellow-400',
    'under_review': 'bg-orange-400',
    'completed': 'bg-green-400'
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

const formatStatus = (status) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown size'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
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

.line-through {
  text-decoration: line-through;
}
</style>