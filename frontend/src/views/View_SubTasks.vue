<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <div v-if="parentTask">
              <h1 class="text-xl font-semibold text-gray-900">Subtasks</h1>
              <router-link :to="`/tasks/${parentTask.id}`">for "<a class="text-sm text-blue-600">{{ parentTask.title }}"</a></router-link>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-4">
            <button @click="fetchSubtasks"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                </path>
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- Create Subtask Button -->
      <div class="mb-6 px-4 sm:px-0">
        <button @click="showCreateForm = !showCreateForm"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          {{ showCreateForm ? 'Cancel' : 'Create New Subtask' }}
        </button>
      </div>

      <!-- Create Subtask Form -->
      <div class="px-4 sm:px-0">
        <TaskForm v-if="showCreateForm" title="Create New Subtask" :is-subtask="true" :is-submitting="isCreating"
          submit-button-text="Create Subtask" submit-button-loading-text="Creating..." @submit="createSubtask"
          @cancel="showCreateForm = false" />
      </div>

      <div class="px-4 py-6 sm:px-0">
        <!-- Task Overview Card -->
        <div v-if="parentTask" class="bg-white overflow-hidden shadow rounded-lg mb-6">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-lg font-medium text-gray-900">{{ parentTask.title }}</h2>
                <p v-if="parentTask.description" class="mt-1 text-sm text-gray-600">{{ parentTask.description }}</p>
              </div>
              <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusBadgeColor(parentTask.status)">
                  {{ parentTask.status }}
                </span>
                <router-link :to="`/tasks/${parentTask.id}`"
                  class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                  View Full Task →
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p class="mt-2 text-gray-600">Loading subtasks...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error loading subtasks</h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Subtasks List -->
        <div v-else-if="subtasks.length > 0" class="space-y-3">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">Subtasks ({{ subtasks.length }})</h3>
            <div class="flex space-x-2">
              <span class="text-sm text-gray-500">
                {{ completedCount }}/{{ subtasks.length }} completed
              </span>
              <div class="w-24 bg-gray-200 rounded-full h-2 mt-1">
                <div class="bg-green-600 h-2 rounded-full" :style="{ width: progressPercentage + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- Subtasks Grid using TaskCard -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="subtask in subtasks" :key="subtask.id" class="relative">
              <TaskCard :task="subtask" @view="viewSubtaskDetails" @edit="editSubtask" @delete="deleteSubtask" />

              <!-- Loading indicator overlay -->
              <div v-if="updatingSubtaskId === subtask.id"
                class="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center rounded-lg">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4">
            </path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No subtasks found</h3>
          <p class="mt-1 text-sm text-gray-500">This task doesn't have any subtasks yet.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TaskCard from '@/components/TaskCard.vue'
import TaskForm from '@/components/TaskForm.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const subtasks = ref([])
const parentTask = ref(null)
const loading = ref(true)
const error = ref(null)
const showCreateForm = ref(false)
const isCreating = ref(false)
const updatingSubtaskId = ref(null)

const KONG_API_URL = "http://localhost:8000"

// Computed properties for progress tracking
const completedCount = computed(() => {
  return subtasks.value.filter(subtask => subtask.status === 'Completed').length
})

const progressPercentage = computed(() => {
  if (subtasks.value.length === 0) return 0
  return Math.round((completedCount.value / subtasks.value.length) * 100)
})

// Function to fetch parent task details
async function fetchParentTask() {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch task: ${response.status}`)
    }

    parentTask.value = await response.json()
  } catch (err) {
    console.error('Error fetching parent task:', err)
  }
}

// Function to fetch subtasks
async function fetchSubtasks() {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Task not found')
      }
      throw new Error(`Failed to fetch subtasks: ${response.status}`)
    }

    subtasks.value = await response.json()
  } catch (err) {
    console.error('Error fetching subtasks:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Function to create subtask
async function createSubtask(formData) {
  try {
    isCreating.value = true

    const subtaskData = {
      title: formData.title,
      status: formData.status
    }

    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(subtaskData)
    })

    if (response.ok) {
      await fetchSubtasks()
      showCreateForm.value = false
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || `Failed to create subtask: ${response.status}`)
    }
  } catch (err) {
    console.error('Error creating subtask:', err)
    alert('Failed to create subtask: ' + err.message)
  } finally {
    isCreating.value = false
  }
}

// Function to view subtask details
function viewSubtaskDetails(subtaskId) {
  router.push(`/tasks/${route.params.id}/subtasks/${subtaskId}`)
}

// Function to edit subtask
function editSubtask(subtask) {
  console.log('Edit subtask:', subtask)
}

// Function to delete subtask
async function deleteSubtask(subtaskId) {
  if (!confirm('Are you sure you want to delete this subtask?')) return

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks/${subtaskId}`, {
      method: 'DELETE'
    })

    if (response.ok || response.status === 404) {
      await fetchSubtasks()
    } else {
      throw new Error(`Failed to delete subtask: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting subtask:', err)
    alert('Failed to delete subtask: ' + err.message)
  }
}

// Function to get status badge color (for parent task)
function getStatusBadgeColor(status) {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    'Completed': 'bg-green-100 text-green-800',
    'On Hold': 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

// Initialize component
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchParentTask()
  fetchSubtasks()
})
</script>

<style scoped>
.line-through {
  text-decoration: line-through;
}
</style>