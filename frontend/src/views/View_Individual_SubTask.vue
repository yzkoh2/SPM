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
              <div class="mt-1 text-sm text-blue-700 flex items-center space-x-4">
                <span>Owner: User {{ parentTask.owner_id }}</span>
                <span v-if="parentTask.assigned_to">Assigned: User {{ parentTask.assigned_to }}</span>
                <span v-else class="text-orange-700">Unassigned</span>
              </div>
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
                {{ formatStatus(subtask.status) }}
              </span>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button @click="showAssignmentDialog" 
                      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                {{ subtask.assigned_to ? 'Reassign' : 'Assign' }}
              </button>
              <button @click="toggleComplete" 
                      :class="subtask.status === 'completed' ? 'bg-orange-600 hover:bg-orange-700' : 'bg-green-600 hover:bg-green-700'"
                      class="text-white px-4 py-2 rounded-md text-sm font-medium">
                {{ subtask.status === 'completed' ? 'Mark Incomplete' : 'Mark Complete' }}
              </button>
              <button @click="editSubtask" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Edit
              </button>
              <button @click="deleteSubtask" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Delete
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
          <div class="mt-6 grid grid-cols-1 md:grid-cols-4 gap-6 pt-6 border-t border-gray-200">
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Status</h4>
              <p class="mt-1 text-lg text-gray-900">{{ formatStatus(subtask.status) }}</p>
              <p class="text-xs text-gray-500">{{ subtask.is_completed ? 'Completed' : 'In Progress' }}</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Assigned To</h4>
              <p class="mt-1 text-lg text-gray-900">
                {{ subtask.assigned_to ? `User ${subtask.assigned_to}` : 'Unassigned' }}
              </p>
              <p v-if="!subtask.assigned_to" class="text-xs text-orange-600">Available for assignment</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Created</h4>
              <p class="mt-1 text-lg text-gray-900">{{ formatDate(subtask.created_at) }}</p>
              <p class="text-xs text-gray-500">by User {{ subtask.created_by }}</p>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Order</h4>
              <p class="mt-1 text-lg text-gray-900">#{{ subtask.order_index }}</p>
              <p class="text-xs text-gray-500">in sequence</p>
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
              <option value="unassigned">Unassigned</option>
              <option value="ongoing">Ongoing</option>
              <option value="under_review">Under Review</option>
              <option value="completed">Completed</option>
            </select>
            <div v-if="statusUpdateLoading" class="flex items-center text-sm text-gray-500">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
              Updating...
            </div>
          </div>
          
          <!-- Assignment Status -->
          <div class="mt-4 p-4 bg-gray-50 rounded-md">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-medium text-gray-700">Assignment Status</h4>
                <p class="text-sm text-gray-600">
                  {{ subtask.assigned_to ? `Currently assigned to User ${subtask.assigned_to}` : 'Not assigned to anyone' }}
                </p>
              </div>
              <button @click="showAssignmentDialog"
                      class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1 rounded-md text-sm">
                {{ subtask.assigned_to ? 'Reassign' : 'Assign' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Activity Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Comments</p>
                <p class="text-2xl font-semibold text-gray-900">{{ subtask.comments?.length || 0 }}</p>
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
                <p class="text-2xl font-semibold text-gray-900">{{ subtask.attachments?.length || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900">Comments ({{ subtask.comments?.length || 0 }})</h3>
            <button @click="showAddCommentDialog = true"
                    class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              Add Comment
            </button>
          </div>
          
          <div v-if="subtask.comments && subtask.comments.length > 0" class="space-y-4">
            <div v-for="comment in subtask.comments" :key="comment.id" 
                 class="border-l-4 border-indigo-200 pl-4 py-2">
              <p class="text-gray-700">{{ comment.content }}</p>
              <p class="text-xs text-gray-500 mt-1">
                User {{ comment.created_by }} • {{ formatDate(comment.created_at) }}
                <span v-if="comment.updated_at && comment.updated_at !== comment.created_at">
                  • Edited {{ formatDate(comment.updated_at) }}
                </span>
              </p>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
            <p class="mb-4">No comments yet</p>
            <button @click="showAddCommentDialog = true"
                    class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              Add First Comment
            </button>
          </div>
        </div>

        <!-- Attachments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900">Attachments ({{ subtask.attachments?.length || 0 }})</h3>
            <button @click="showAddAttachmentDialog = true"
                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              Add Attachment
            </button>
          </div>
          
          <div v-if="subtask.attachments && subtask.attachments.length > 0" class="space-y-3">
            <div v-for="attachment in subtask.attachments" :key="attachment.id" 
                 class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                </svg>
                <div>
                  <span class="text-gray-900">{{ attachment.file_name }}</span>
                  <p class="text-xs text-gray-500">
                    {{ formatFileSize(attachment.file_size) }} • {{ attachment.mime_type }} 
                    • Uploaded {{ formatDate(attachment.uploaded_at) }}
                  </p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <a :href="attachment.file_path" target="_blank" 
                   class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                  Download
                </a>
                <button @click="deleteAttachment(attachment.id)"
                        class="text-red-600 hover:text-red-500 text-sm font-medium">
                  Delete
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
            </svg>
            <p class="mb-4">No attachments</p>
            <button @click="showAddAttachmentDialog = true"
                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              Add First Attachment
            </button>
          </div>
        </div>
      </div>

      <!-- Assignment Dialog -->
      <div v-if="showAssignDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ subtask?.assigned_to ? 'Reassign Subtask' : 'Assign Subtask' }}
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            Subtask: "{{ subtask?.title }}"
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
            <button @click="assignSubtask" :disabled="!assignmentUserId"
                    class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
              Assign
            </button>
          </div>
        </div>
      </div>

      <!-- Add Comment Dialog -->
      <div v-if="showAddCommentDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add Comment</h3>
          
          <form @submit.prevent="addComment">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Comment</label>
              <textarea 
                v-model="newComment" 
                rows="4" 
                required
                placeholder="Enter your comment..."
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </textarea>
            </div>
            
            <div class="flex justify-end space-x-3 mt-4">
              <button type="button" @click="cancelAddComment" 
                      class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
                Cancel
              </button>
              <button type="submit" :disabled="!newComment.trim()"
                      class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
                Add Comment
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Add Attachment Dialog -->
      <div v-if="showAddAttachmentDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Add Attachment</h3>
          
          <form @submit.prevent="addAttachment">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">File Name</label>
                <input 
                  v-model="newAttachment.file_name" 
                  type="text" 
                  required
                  placeholder="Enter file name"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">File Path/URL</label>
                <input 
                  v-model="newAttachment.file_path" 
                  type="text" 
                  required
                  placeholder="Enter file path or URL"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">File Size (bytes)</label>
                  <input 
                    v-model="newAttachment.file_size" 
                    type="number"
                    placeholder="File size in bytes"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">MIME Type</label>
                  <input 
                    v-model="newAttachment.mime_type" 
                    type="text"
                    placeholder="e.g., application/pdf"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button type="button" @click="cancelAddAttachment" 
                      class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
                Cancel
              </button>
              <button type="submit" :disabled="!newAttachment.file_name || !newAttachment.file_path"
                      class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md disabled:opacity-50">
                Add Attachment
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
const subtask = ref(null)
const parentTask = ref(null)
const loading = ref(true)
const error = ref(null)
const statusUpdateLoading = ref(false)

// Dialogs
const showAssignDialog = ref(false)
const showAddCommentDialog = ref(false)
const showAddAttachmentDialog = ref(false)

// Form data
const assignmentUserId = ref('')
const newComment = ref('')
const newAttachment = ref({
  file_name: '',
  file_path: '',
  file_size: null,
  mime_type: ''
})

// API configuration
const KONG_API_URL = "http://localhost:8000"
const currentUserId = 1

// Fetch subtask details from API
const fetchSubtaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const taskId = route.params.id
    const subtaskId = route.params.subtaskId
    
    // Fetch subtask details
    const subtaskResponse = await fetch(`${KONG_API_URL}/subtasks/${subtaskId}`, {
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
    
    const response = await fetch(`${KONG_API_URL}/subtasks/${route.params.subtaskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: newStatus,
        updated_by: currentUserId
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

// Toggle completion
const toggleComplete = async () => {
  const newStatus = subtask.value.status === 'completed' ? 'ongoing' : 'completed'
  await updateSubtaskStatus(newStatus)
}

// Assignment methods
const showAssignmentDialog = () => {
  assignmentUserId.value = subtask.value.assigned_to || ''
  showAssignDialog.value = true
}

const assignSubtask = async () => {
  if (!assignmentUserId.value) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/subtasks/${subtask.value.id}/assign`, {
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
      await fetchSubtaskDetails()
      showAssignDialog.value = false
      assignmentUserId.value = ''
      alert('Subtask assigned successfully!')
    } else {
      throw new Error(`Failed to assign subtask: ${response.status}`)
    }
  } catch (err) {
    console.error('Error assigning subtask:', err)
    alert('Failed to assign subtask: ' + err.message)
  }
}

// Comment methods
const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/subtasks/${subtask.value.id}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: newComment.value.trim(),
        created_by: currentUserId
      })
    })
    
    if (response.ok) {
      await fetchSubtaskDetails()
      cancelAddComment()
      alert('Comment added successfully!')
    } else {
      throw new Error(`Failed to add comment: ${response.status}`)
    }
  } catch (err) {
    console.error('Error adding comment:', err)
    alert('Failed to add comment: ' + err.message)
  }
}

const cancelAddComment = () => {
  showAddCommentDialog.value = false
  newComment.value = ''
}

// Attachment methods
const addAttachment = async () => {
  if (!newAttachment.value.file_name || !newAttachment.value.file_path) return
  
  try {
    const attachmentData = {
      file_name: newAttachment.value.file_name,
      file_path: newAttachment.value.file_path,
      uploaded_by: currentUserId
    }
    
    if (newAttachment.value.file_size) {
      attachmentData.file_size = parseInt(newAttachment.value.file_size)
    }
    
    if (newAttachment.value.mime_type) {
      attachmentData.mime_type = newAttachment.value.mime_type
    }
    
    const response = await fetch(`${KONG_API_URL}/subtasks/${subtask.value.id}/attachments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(attachmentData)
    })
    
    if (response.ok) {
      await fetchSubtaskDetails()
      cancelAddAttachment()
      alert('Attachment added successfully!')
    } else {
      throw new Error(`Failed to add attachment: ${response.status}`)
    }
  } catch (err) {
    console.error('Error adding attachment:', err)
    alert('Failed to add attachment: ' + err.message)
  }
}

const cancelAddAttachment = () => {
  showAddAttachmentDialog.value = false
  newAttachment.value = {
    file_name: '',
    file_path: '',
    file_size: null,
    mime_type: ''
  }
}

const deleteAttachment = async (attachmentId) => {
  if (!confirm('Are you sure you want to delete this attachment?')) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/attachments/${attachmentId}`, {
      method: 'DELETE'
    })
    
    if (response.ok || response.status === 404) {
      await fetchSubtaskDetails()
      alert('Attachment deleted successfully!')
    } else {
      throw new Error(`Failed to delete attachment: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting attachment:', err)
    alert('Failed to delete attachment: ' + err.message)
  }
}

// Action methods
const editSubtask = () => {
  console.log('Edit subtask:', subtask.value)
  alert('Edit functionality coming soon!')
}

const deleteSubtask = async () => {
  if (!confirm('Are you sure you want to delete this subtask? This action cannot be undone.')) {
    return
  }
  
  try {
    const response = await fetch(`${KONG_API_URL}/subtasks/${route.params.subtaskId}`, {
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