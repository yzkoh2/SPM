<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link
            :to="`/projects/${route.params.id}`"
            class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              ></path>
            </svg>
            Back to Project Dashboard
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">All Project Tasks</h1>
            <p v-if="project" class="text-sm text-gray-600 mt-1">{{ project.title }}</p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div
          class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0"
        >
          <div
            class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
              <select
                v-model="filters.status"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Statuses</option>
                <option value="Unassigned">Unassigned</option>
                <option value="Ongoing">Ongoing</option>
                <option value="Under Review">Under Review</option>
                <option value="Completed">Completed</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >Filter by Priority</label
              >
              <select
                v-model="filters.priority"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Priorities</option>
                <option value="high">High (8-10)</option>
                <option value="medium">Medium (4-7)</option>
                <option value="low">Low (1-3)</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sort by</label>
              <select
                v-model="sortBy"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="default">Default Order</option>
                <option value="deadline-earliest">Deadline (Earliest First)</option>
                <option value="deadline-latest">Deadline (Latest First)</option>
                <option value="priority-highest">Priority (Highest First)</option>
                <option value="priority-lowest">Priority (Lowest First)</option>
              </select>
            </div>
          </div>

          <div
            class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4"
          >
            <button
              @click="clearFilters"
              class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              Clear Filters
            </button>
            <button
              @click="fetchTasks"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-gray-600">Loading tasks...</p>
      </div>

      <div v-else-if="error" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading tasks</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="tasks.length > 0" class="space-y-3">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">
              Tasks ({{ filteredTasks.length
              }}{{ filteredTasks.length !== tasks.length ? ` of ${tasks.length}` : '' }})
            </h3>
            <div class="flex space-x-2">
              <span class="text-sm text-gray-500">
                {{ completedCount }}/{{ tasks.length }} completed
              </span>
              <div class="w-24 bg-gray-200 rounded-full h-2 mt-1">
                <div
                  class="bg-green-600 h-2 rounded-full"
                  :style="{ width: progressPercentage + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="task in filteredTasks" :key="task.id" class="relative">
              <TaskCard
                :task="task"
                @view="viewTaskDetails"
                @edit="editTask"
                @delete="deleteTask"
              />

              <div
                v-if="updatingTaskId === task.id"
                class="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center rounded-lg"
              >
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            </div>
          </div>

          <!-- Show message if filters hide all tasks -->
          <div v-if="filteredTasks.length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-600">No tasks match the current filters.</p>
            <button
              @click="clearFilters"
              class="mt-2 text-sm text-indigo-600 hover:text-indigo-500"
            >
              Clear filters
            </button>
          </div>
      </div>

      <div v-else class="text-center py-12">
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          ></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No tasks found</h3>
        <p class="mt-1 text-sm text-gray-500">This project doesn't have any tasks yet.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TaskCard from '@/components/TaskCard.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const tasks = ref([])
const project = ref(null)
const loading = ref(true)
const error = ref(null)
const updatingTaskId = ref(null)

const filters = ref({
  status: '',
  priority: '',
})

const sortBy = ref('default')

const KONG_API_URL = 'http://localhost:8000'

// Computed properties for progress tracking
const completedCount = computed(() => {
  return tasks.value.filter((task) => task.status === 'Completed').length
})

const progressPercentage = computed(() => {
  if (tasks.value.length === 0) return 0
  return Math.round((completedCount.value / tasks.value.length) * 100)
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  // Filter by status
  if (filters.value.status) {
    filtered = filtered.filter((task) => task.status === filters.value.status)
  }

  // Filter by priority
  if (filters.value.priority) {
    filtered = filtered.filter((task) => {
      const priority = task.priority || 5

      switch (filters.value.priority) {
        case 'high':
          return priority >= 8 && priority <= 10
        case 'medium':
          return priority >= 4 && priority <= 7
        case 'low':
          return priority >= 1 && priority <= 3
        default:
          return true
      }
    })
  }

  // Apply sorting
  if (sortBy.value === 'deadline-earliest') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(a.deadline) - new Date(b.deadline)
    })
  } else if (sortBy.value === 'deadline-latest') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(b.deadline) - new Date(a.deadline)
    })
  } else if (sortBy.value === 'priority-highest') {
    filtered.sort((a, b) => {
      const priorityA = a.priority || 5
      const priorityB = b.priority || 5
      return priorityB - priorityA
    })
  } else if (sortBy.value === 'priority-lowest') {
    filtered.sort((a, b) => {
      const priorityA = a.priority || 5
      const priorityB = b.priority || 5
      return priorityA - priorityB
    })
  }

  return filtered
})

// Function to fetch project details
async function fetchProject() {
  try {
    const response = await fetch(
      `${KONG_API_URL}/projects/${route.params.id}?user_id=${authStore.currentUserId}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch project: ${response.status}`)
    }

    project.value = await response.json()
  } catch (err) {
    console.error('Error fetching project:', err)
  }
}

// Function to fetch tasks
async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const response = await fetch(
      `${KONG_API_URL}/projects/${route.params.id}/dashboard?user_id=${authStore.currentUserId}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    )

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Project not found')
      }
      throw new Error(`Failed to fetch tasks: ${response.status}`)
    }

    const data = await response.json()
    tasks.value = data.tasks || []
  } catch (err) {
    console.error('Error fetching tasks:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Function to view task details
function viewTaskDetails(taskId) {
  router.push(`/tasks/${taskId}?fromProjectTasks=${route.params.id}`)
}

// Function to edit task
function editTask(task) {
  if (authStore.user.id != task.owner_id) {
    alert('You do not have permission to edit the task.')
    return
  }
  // Navigate to task details page which has edit functionality
  router.push(`/tasks/${task.id}`)
}

// Function to delete task
async function deleteTask(taskId) {
  if (!confirm('Are you sure you want to delete this task?')) return

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: authStore.user.id,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      alert(data.message || 'Task deleted successfully')
      await fetchTasks()
    } else {
      throw new Error(data.error || `Failed to delete task: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting task:', err)
    alert('Failed to delete task: ' + err.message)
  }
}

const applyFilters = () => {}

const clearFilters = () => {
  filters.value.status = ''
  filters.value.priority = ''
  sortBy.value = 'default'
}

// Initialize component
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await fetchProject()
  await fetchTasks()
})
</script>

<style scoped>
.line-through {
  text-decoration: line-through;
}
</style>
