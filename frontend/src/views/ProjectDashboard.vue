<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center">
          <router-link to="/projects"
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Projects
          </router-link>
          <div v-if="!loading && project">
            <h1 class="text-2xl font-bold text-gray-900">{{ project.title }}</h1>
            <p class="text-sm text-gray-500 mt-1">{{ project.description }}</p>
          </div>
        </div>
      </div>
    </div>

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
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
        <button @click="loadDashboard" class="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm">
          Try Again
        </button>
      </div>

      <!-- Dashboard Content -->
      <div v-else>
        <!-- Project Info & Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Total Tasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ tasks.length }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Completed</p>
                <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('Completed') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-yellow-100 rounded-lg">
                <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">In Progress</p>
                <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('Ongoing') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-purple-100 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Collaborators</p>
                <p class="text-2xl font-semibold text-gray-900">{{ collaborators.length }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Filters and Sorting -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 class="text-lg font-semibold mb-4">Filters & Sorting</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Status Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Status</label>
              <div class="space-y-2">
                <label v-for="status in availableStatuses" :key="status" class="flex items-center">
                  <input type="checkbox" :value="status" v-model="filters.statuses"
                         @change="applyFilters"
                         class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
                  <span class="ml-2 text-sm text-gray-700">{{ status }}</span>
                </label>
              </div>
            </div>

            <!-- Role Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Role</label>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="radio" value="" v-model="filters.role" @change="applyFilters"
                         class="border-gray-300 text-indigo-600 focus:ring-indigo-500">
                  <span class="ml-2 text-sm text-gray-700">All Tasks</span>
                </label>
                <label class="flex items-center">
                  <input type="radio" value="owner" v-model="filters.role" @change="applyFilters"
                         class="border-gray-300 text-indigo-600 focus:ring-indigo-500">
                  <span class="ml-2 text-sm text-gray-700">My Tasks (Owner)</span>
                </label>
                <label class="flex items-center">
                  <input type="radio" value="collaborator" v-model="filters.role" @change="applyFilters"
                         class="border-gray-300 text-indigo-600 focus:ring-indigo-500">
                  <span class="ml-2 text-sm text-gray-700">Collaborating</span>
                </label>
              </div>
            </div>

            <!-- Sort By -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select v-model="filters.sortBy" @change="applyFilters"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                <option value="deadline">Deadline</option>
                <option value="title">Title</option>
                <option value="status">Status</option>
                <option value="priority">Priority</option>
              </select>
            </div>
          </div>

          <!-- Clear Filters -->
          <div class="mt-4">
            <button @click="clearFilters" class="text-sm text-indigo-600 hover:text-indigo-500 font-medium">
              Clear all filters
            </button>
          </div>
        </div>

        <!-- Tasks List -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold mb-4">Tasks ({{ tasks.length }})</h3>
          
          <!-- Empty State -->
          <div v-if="tasks.length === 0" class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No tasks found</h3>
            <p class="mt-1 text-sm text-gray-500">Try adjusting your filters or create a new task.</p>
          </div>

          <!-- Tasks Grid -->
          <div v-else class="space-y-4">
            <div v-for="task in tasks" :key="task.id"
                 class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                 @click="viewTaskDetails(task.id)">
              <div class="flex justify-between items-start mb-2">
                <h4 class="text-lg font-semibold text-gray-900">{{ task.title }}</h4>
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', getStatusBadgeColor(task.status)]">
                  {{ task.status }}
                </span>
              </div>

              <p v-if="task.description" class="text-sm text-gray-600 mb-3 line-clamp-2">{{ task.description }}</p>

              <div class="flex flex-wrap gap-4 text-xs text-gray-600">
                <div class="flex items-center" :class="getDeadlineColor(task.deadline)">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  {{ formatDeadline(task.deadline) }}
                </div>
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                  </svg>
                  {{ task.subtask_count || 0 }} subtasks
                </div>
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
                  </svg>
                  {{ task.comment_count || 0 }} comments
                </div>
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  {{ (task.collaborator_ids?.length || 0) }} collaborators
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const KONG_API_URL = "http://localhost:8000"

// Reactive data
const loading = ref(false)
const error = ref(null)
const project = ref(null)
const tasks = ref([])
const collaborators = ref([])

const filters = ref({
  statuses: [],
  role: '', // '', 'owner', or 'collaborator'
  sortBy: 'deadline'
})

const availableStatuses = ['Unassigned', 'Ongoing', 'Under Review', 'Completed']

// Computed
const getTaskCountByStatus = (status) => {
  return tasks.value.filter(task => task.status === status).length
}

// Helper functions
const getStatusBadgeColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-blue-100 text-blue-800',
    'Under Review': 'bg-yellow-100 text-yellow-800',
    'Completed': 'bg-green-100 text-green-800'
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
  if (!deadline) return 'No deadline'
  const date = new Date(deadline)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// API functions
const loadDashboard = async () => {
  try {
    loading.value = true
    error.value = null
    
    const projectId = route.params.id
    const userId = authStore.currentUserId
    
    // Build query parameters
    const params = new URLSearchParams({
      user_id: userId
    })
    
    if (filters.value.statuses.length > 0) {
      params.append('status', filters.value.statuses.join(','))
    }
    
    if (filters.value.role === 'owner') {
      params.append('owner', 'me')
    } else if (filters.value.role === 'collaborator') {
      params.append('collaborator', 'me')
    }
    
    params.append('sort_by', filters.value.sortBy)
    
    // Fetch dashboard data
    const response = await fetch(`${KONG_API_URL}/projects/${projectId}/dashboard?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to load dashboard')
    }
    
    const data = await response.json()
    
    project.value = data.project
    tasks.value = data.tasks
    collaborators.value = data.collaborators
    
  } catch (err) {
    console.error('Error loading dashboard:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  loadDashboard()
}

const clearFilters = () => {
  filters.value = {
    statuses: [],
    role: '',
    sortBy: 'deadline'
  }
  loadDashboard()
}

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

// Lifecycle
onMounted(() => {
  loadDashboard()
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