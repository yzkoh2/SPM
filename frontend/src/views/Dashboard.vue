<template>
  <div class="min-h-screen bg-gray-50">

    <!-- Page Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Task Dashboard</h1>
        <p class="text-sm text-gray-600 mt-1">Manage your tasks and collaborate with your team</p>
      </div>

      <!-- Create Task Button -->
      <div class="mb-6">
        <button @click="showCreateForm = !showCreateForm" 
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          {{ showCreateForm ? 'Cancel' : 'Create New Task' }}
        </button>
      </div>

      <!-- Create Task Form -->
      <TaskForm
        v-if="showCreateForm"
        title="Create New Task"
        :is-submitting="isCreating"
        submit-button-text="Create Task"
        submit-button-loading-text="Creating..."
        @submit="createTask"
        @cancel="showCreateForm = false"
      />

      <!-- Filters and Sorting -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
              <select v-model="filters.status" @change="applyFilters"
                      class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">All Statuses</option>
                <option value="Unassigned">Unassigned</option>
                <option value="Ongoing">Ongoing</option>
                <option value="Under Review">Under Review</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Deadline</label>
              <select v-model="filters.deadline" @change="applyFilters"
                      class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">All Deadlines</option>
                <option value="overdue">Overdue</option>
                <option value="today">Due Today</option>
                <option value="week">Due This Week</option>
                <option value="month">Due This Month</option>
              </select>
            </div>
          </div>
          
          <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
            <button @click="clearFilters" 
                    class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors">
              Clear Filters
            </button>
            <button @click="fetchTasks(authStore.user.id)" 
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors">
              Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Task Statistics -->
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
            <div class="p-2 bg-gray-100 rounded-lg">
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Unassigned</p>
              <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('Unassigned') }}</p>
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
              <p class="text-sm font-medium text-gray-600">Ongoing</p>
              <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('Ongoing') }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Completed</p>
              <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('Completed') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3 class="text-lg font-medium text-red-800">Backend Connection Error</h3>
        </div>
        <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
        <div class="mt-4 space-x-2">
          <button @click="fetchTasks" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md">
            Try Again
          </button>
        </div>
      </div>

      <!-- Tasks Grid -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
      
      <div v-else-if="tasks.length === 0 && !error" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No tasks found</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating your first task.</p>
      </div>
      
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          @view="viewTaskDetails"
          @edit="editTask"
          @delete="deleteTask"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TaskCard from '@/components/TaskCard.vue'
import TaskForm from '@/components/TaskForm.vue'

const router = useRouter()
const authStore = useAuthStore()

// Reactive data
const tasks = ref([])
const loading = ref(true)
const showCreateForm = ref(false)
const isCreating = ref(false)
const error = ref(null)
const role = ref(null)

// Filters
const filters = ref({
  status: '',
  deadline: ''
})

// API configuration
const KONG_API_URL = "http://localhost:8000"

// Computed properties
const filteredTasks = computed(() => {
  let filtered = [...tasks.value]
  
  if (filters.value.status) {
    filtered = filtered.filter(task => task.status === filters.value.status)
  }
  
  if (filters.value.deadline && filters.value.deadline !== '') {
    const now = new Date()
    filtered = filtered.filter(task => {
      if (!task.deadline) return false
      const deadline = new Date(task.deadline)
      
      switch (filters.value.deadline) {
        case 'overdue':
          return deadline < now
        case 'today':
          return deadline.toDateString() === now.toDateString()
        case 'week':
          const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
          return deadline >= now && deadline <= weekFromNow
        case 'month':
          const monthFromNow = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
          return deadline >= now && deadline <= monthFromNow
        default:
          return true
      }
    })
  }
  
  return filtered
})

// Methods
const fetchTasks = async (userID) => {
  try {
    loading.value = true
    error.value = null

    const queryParam = new URLSearchParams()
    if (userID) {
      queryParam.append('owner_id', userID) 
    }
    
    const response = await fetch(`${KONG_API_URL}/tasks${queryParam.toString() ? `?${queryParam.toString()}` : ''}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      tasks.value = data
    } else {
      const errorText = await response.text()
      throw new Error(`API Error: ${response.status} - ${errorText}`)
    }
  } catch (err) {
    console.error('Error fetching tasks:', err)
    error.value = `Failed to fetch tasks: ${err.message}`
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const createTask = async (formData) => {
  try {
    isCreating.value = true
    error.value = null
    
    const taskData = {
      title: formData.title,
      description: formData.description || null,
      deadline: formData.deadline || null,
      status: formData.status,
      owner_id: authStore.currentUserId
    }
    
    const response = await fetch(`${KONG_API_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskData)
    })
    
    if (response.ok) {
      await fetchTasks(authStore.user.id)
      showCreateForm.value = false
    } else {
      const errorText = await response.text()
      throw new Error(`Failed to create task: ${response.status} - ${errorText}`)
    }
  } catch (err) {
    console.error('Error creating task:', err)
    alert('Failed to create task: ' + err.message)
  } finally {
    isCreating.value = false
  }
}

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const deleteTask = async (taskId) => {
  if (!confirm('Are you sure you want to delete this task?')) return
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}`, {
      method: 'DELETE'
    })
    
    if (response.ok || response.status === 404) {
      await fetchTasks(authStore.user.id)
    } else {
      throw new Error(`Failed to delete task: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting task:', err)
    alert('Failed to delete task: ' + err.message)
  }
}

const editTask = (task) => {
  console.log('Edit task:', task)
}

const applyFilters = () => {
  // Filters are applied automatically via computed property
}

const clearFilters = () => {
  filters.value.status = ''
  filters.value.deadline = ''
}

const getTaskCountByStatus = (status) => {
  return tasks.value.filter(task => task.status === status).length
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchTasks(authStore.user.id)
    role.value = authStore.user.role
  } else {
    authStore.logout()
  }
})
</script>