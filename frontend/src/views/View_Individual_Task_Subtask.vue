<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with Back Navigation -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link :to="isSubtask ? `/tasks/${parentTaskId}/subtasks` : '/'"
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            {{ isSubtask ? 'Back to Subtasks' : 'Back to Tasks' }}
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">{{ isSubtask ? 'Subtask Details' : 'Task Details' }}</h1>
          </div>
        </div>
      </div>
    </header>

    <!-- Status Update Modal - Only render when task is loaded -->
    <StatusUpdateModal v-if="task && showStatusModal" :show="showStatusModal" :task="task"
      @close="showStatusModal = false" @update-status="handleStatusUpdate" />

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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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

      <!-- Parent Task Reference -->
      <div v-if="isSubtask && parentTask" class="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-900">Part of:</p>
            <h3 class="text-lg font-semibold text-blue-800">{{ parentTask.title }}</h3>
          </div>
          <router-link :to="`/tasks/${parentTaskId}`" class="text-blue-600 hover:text-blue-500 text-sm font-medium">
            View Parent Task →
          </router-link>
        </div>
      </div>

      <!-- Task Details -->
      <div v-if="task" class="space-y-6">
        <!-- Task Header Card -->
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4" :class="getStatusBorderColor(task.status)">
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <h2 class="text-3xl font-bold text-gray-900 mb-2">{{ task.title }}</h2>
              <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                  :class="getStatusBadgeColor(task.status)">
                  {{ task.status }}
                </span>
                <span v-if="canEditTask" class="text-xs text-gray-500 flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  You can edit this task
                </span>
              </div>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button @click="showStatusModal = true"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                  </path>
                </svg>
                Update Status
              </button>
              <button v-if="canEditTask" @click="editTask"
                class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                {{ isSubtask ? 'Edit Subtask' : 'Edit Task' }}
              </button>
              <button @click="deleteTask"
                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium">
                Delete
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
            <div v-if="!isSubtask">
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Progress</h4>
              <div class="mt-1 flex items-center">
                <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                  <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    :style="{ width: getTaskProgress() + '%' }"></div>
                </div>
                <span class="text-sm text-gray-600">{{ getTaskProgress() }}%</span>
              </div>
            </div>
          </div>

          <!-- Collaborators Section -->
          <div v-if="collaboratorDetails.length > 0" class="mt-6 pt-6 border-t border-gray-200">
            <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">Collaborators</h4>
            <div class="flex flex-wrap gap-2">
              <div v-for="collab in collaboratorDetails" :key="collab.user_id"
                class="inline-flex items-center px-3 py-2 rounded-full text-sm bg-indigo-50 text-indigo-700">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                {{ collab.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 gap-6" :class="isSubtask ? 'md:grid-cols-2' : 'md:grid-cols-3'">
          <div v-if="!isSubtask" class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2">
                  </path>
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
                  </path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Comments</p>
                <p class="text-2xl font-semibold text-gray-900">{{ totalCommentCount }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-purple-100 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13">
                  </path>
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
        <div v-if="!isSubtask" class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900">Subtasks ({{ task.subtasks?.length || 0 }})</h3>
            <router-link :to="`/tasks/${task.id}/subtasks`"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              View All Subtasks
            </router-link>
          </div>

          <div v-if="task.subtasks && task.subtasks.length > 0" class="space-y-3">
            <div v-for="subtask in task.subtasks.slice(0, 5)" :key="subtask.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
              @click="$router.push(`/tasks/${task.id}/subtasks/${subtask.id}`)">
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
              <router-link :to="`/tasks/${task.id}/subtasks`"
                class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                View {{ task.subtasks.length - 5 }} more subtasks →
              </router-link>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2">
              </path>
            </svg>
            <p>No subtasks yet</p>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">
            Comments ({{ totalCommentCount }})
          </h3>

          <!-- Add Comment Form -->
          <div class="mb-6 border-b border-gray-200 pb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Add a Comment</label>

            <Mentionable
              :keys="['@']"
              :items="collaboratorDetails.map(c => ({ value: c.username, label: c.name, user_id: c.user_id, role: c.role }))"
              offset="6"
              insert-space
            >
              <textarea
                v-model="newComment"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Write a comment... Use @ to mention collaborators"
                @keydown.meta.enter="addComment"
                @keydown.ctrl.enter="addComment"
              ></textarea>

              <!-- Custom rendering for @ mentions -->
              <template #item-@="{ item, isSelected }">
                <div 
                  :class="['flex items-center p-2 space-x-3 cursor-pointer rounded-md transition-colors duration-150 ease-in-out', isSelected ? 'bg-indigo-100' : 'hover:bg-gray-50']"
                >
                  <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                  <div class="flex-1">
                    <div class="font-medium text-gray-800">{{ item.label }}</div>
                    <div class="text-sm text-gray-500">{{ item.role }}</div>
                  </div>
                </div>
              </template>

              <template #no-result>
                <div class="text-gray-400 p-2">No users found</div>
              </template>
            </Mentionable>

            <div class="mt-2 flex justify-end">
              <button @click="addComment({ body: newComment})" :disabled="!newComment.trim() || addingComment"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed">
                <span v-if="addingComment">Adding...</span>
                <span v-else>Add Comment</span>
              </button>
            </div>
          </div>

          <!-- Comments List (Nested) -->
          <div v-if="topLevelComments.length > 0" class="space-y-6">
            <CommentItem
              v-for="comment in topLevelComments"
              :key="comment.id"
              :comment="comment"
              :current-user-id="authStore.user?.id"
              :collaborator-details="collaboratorDetails"
              @reply="addComment"
              @delete="handleDeleteComment" />
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
              </path>
            </svg>
            <p>No comments yet. Be the first to comment!</p>
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13">
                  </path>
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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13">
              </path>
            </svg>
            <p>No attachments</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Mentionable } from 'vue-mention'
import 'floating-vue/dist/style.css'
import StatusUpdateModal from '@/components/StatusUpdateModal.vue'
import CommentItem from '@/components/CommentItem.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isSubtask = computed(() => !!route.params.subtaskId)
const taskId = ref(null)
const parentTaskId = ref(null)

if (isSubtask.value) {
  parentTaskId.value = route.params.id
  taskId.value = route.params.subtaskId
  console.log('Viewing as subtask. Parent Task ID:', parentTaskId.value, 'Subtask ID:', taskId.value)
} else {
  taskId.value = route.params.id
  console.log('Viewing as main task. Task ID:', taskId.value)
}

// Reactive data
const task = ref(null)
const parentTask = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const showStatusModal = ref(false)
const newComment = ref('')
const addingComment = ref(false)
const collaborators = ref([])
const collaboratorDetails = ref([])

// API configuration
const KONG_API_URL = "http://localhost:8000"

// Computed properties
const canEditTask = computed(() => {
  if (!task.value || !authStore.user) return false
  return task.value.owner_id === authStore.user.id
})

// Filter to show only top-level comments (no parent)
const topLevelComments = computed(() => {
  return comments.value.filter(comment => !comment.parent_comment_id)
})

// Calculate total comment count including all replies
const totalCommentCount = computed(() => {
  const countComments = (commentsList) => {
    return commentsList.reduce((total, comment) => {
      return total + 1 + (comment.replies ? countComments(comment.replies) : 0)
    }, 0)
  }
  return countComments(comments.value)
})

// Fetch task details from API
const fetchTaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    console.log('Fetching task details for ID:', taskId.value)

    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      task.value = await response.json()
      comments.value = task.value.comments || []
      console.log('Task details loaded:', task.value)
    } else if (response.status === 404) {
      error.value = 'Task not found'
    } else {
      error.value = `Failed to load task: ${response.status}`
    }

    // Fetch parent task details
    if (isSubtask.value && parentTaskId.value) {
      const parentResponse = await fetch(`${KONG_API_URL}/tasks/${parentTaskId.value}`, {
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
    }

    // Fetch collaborator details
    await fetchCollaborators(taskId.value)

  } catch (err) {
    console.error('Error fetching task details:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

const fetchCollaborators = async (taskId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/collaborators`)

    if (response.ok) {
      collaborators.value = await response.json()
      console.log('Task collaborators loaded:', collaborators.value)

      // Fetch details for each collaborator
      const detailsPromises = collaborators.value.map(collab =>
        fetchUserDetails(collab.user_id)
      )

      const details = await Promise.all(detailsPromises)

      // Combine collaborator info with user details
      collaboratorDetails.value = collaborators.value.map((collab, index) => ({
        user_id: collab.user_id,
        name: details[index]?.name || `User ${collab.user_id}`,
        role: details[index]?.role || 'Unknown',
        username: details[index]?.username
      }))

      console.log('Collaborator details loaded:', collaboratorDetails.value)
    } else {
      console.warn('Failed to load collaborators')
      collaboratorDetails.value = []
    }
  } catch (err) {
    console.error('Error fetching collaborators:', err)
    collaboratorDetails.value = []
  }
}

const fetchUserDetails = async (userId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/user/${userId}`)

    if (response.ok) {
      return await response.json()
    } else {
      console.warn(`Failed to load user details for ID ${userId}`)
      return null
    }
  } catch (err) {
    console.error(`Error fetching user ${userId}:`, err)
    return null
  }
}

// Handle status update
const handleStatusUpdate = async ({ newStatus, comment }) => {
  try {
    console.log('Updating task status:', { newStatus, comment, taskId: task.value.id, userId: authStore.user.id })

    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: authStore.user.id,
        status: newStatus
      })
    })

    const data = await response.json()
    console.log('Response:', data)

    if (!response.ok) {
      throw new Error(data.error || 'Failed to update status')
    }

    // Update local task data
    if (data.task) {
      task.value.status = data.task.status
    }

    // Refresh task details to get updated data
    await fetchTaskDetails()

    // Close modal
    showStatusModal.value = false

    // Show success message
    alert('Task status updated successfully!')
  } catch (err) {
    console.error('Error updating status:', err)
    alert('Failed to update status: ' + err.message)
    throw err
  }
}

// Add comment (top-level)
const addComment = async ({body, parentCommentId = null}) => {
  if (!body.trim()) return

  try {
    addingComment.value = true
    
    const mentionRegex = /@(\w+)/g;
    const matches = [...body.matchAll(mentionRegex)];
    const mentionedUsernames = matches.map(match => match[1]);
    const uniqueUsernames = [...new Set(mentionedUsernames)];
    const mention_ids = uniqueUsernames.map(username => {
      const collaborator = collaboratorDetails.value.find(c => c.username === username);
      return collaborator ? collaborator.user_id : null;
    }).filter(id => id !== null);

    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        body: body,
        author_id: authStore.user.id,
        parent_comment_id: parentCommentId,
        mention_ids: mention_ids
      })
    })

    if (response.ok) {
      // Refresh task details to get updated comments with nested structure
      await fetchTaskDetails()
      if (!parentCommentId) {
          newComment.value = ''
      }
      console.log('Comment added successfully')
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add comment')
    }
  } catch (err) {
    console.error('Error adding comment:', err)
    alert('Failed to add comment: ' + err.message)
  } finally {
    addingComment.value = false
  }
}

// Handle delete comment
const handleDeleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) {
    return
  }

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/deletecomment/${commentId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      // Refresh task details to get updated comments
      await fetchTaskDetails()
      console.log('Comment deleted successfully')
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to delete comment')
    }
  } catch (err) {
    console.error('Error deleting comment:', err)
    alert('Failed to delete comment: ' + err.message)
  }
}

// Action methods
const editTask = () => {
  const editRoute = isSubtask.value 
    ? `/tasks/${parentTaskId.value}/subtasks/${taskId.value}/edit`
    : `/tasks/${taskId.value}/edit`
  router.push(editRoute)
}

const deleteTask = async () => {
  if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
    return
  }

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: authStore.user.id
      })
    })

    const data = await response.json()

    if (response.ok) {
      alert(data.message || 'Task deleted successfully')
      if (isSubtask.value) {
        router.push(`/tasks/${parentTaskId.value}/subtasks`)
      } else {
        router.push('/')
      }
    } else {
      throw new Error(data.error || `Failed to delete: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting task:', err)
    alert('Failed to delete task: ' + err.message)
  }
}

// Calculate task progress based on subtasks
const getTaskProgress = () => {
  if (!task.value.subtasks || task.value.subtasks.length === 0) {
    return task.value.status === 'Completed' ? 100 : 0
  }

  const completedCount = task.value.subtasks.filter(s => s.status === 'Completed').length
  return Math.round((completedCount / task.value.subtasks.length) * 100)
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

watch(
  () => [route.params.id, route.params.subtaskId],
  ([newTaskId, newSubtaskId]) => {
    if (isSubtask.value) {
      parentTaskId.value = newTaskId
      taskId.value = newSubtaskId
    } else {
      taskId.value = newTaskId
    }
    fetchTaskDetails()
  }
)

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