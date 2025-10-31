<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Task Dashboard</h1>
        <p class="text-sm text-gray-600 mt-1">Manage your tasks and collaborate with your team</p>
      </div>

      <TaskboardNavigation />

      <div class="mb-6">
        <button
          @click="showCreateForm = !showCreateForm"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            ></path>
          </svg>
          {{ showCreateForm ? 'Cancel' : 'Create New Task' }}
        </button>
      </div>

      <TaskForm
        v-if="showCreateForm"
        title="Create New Task"
        :is-submitting="isCreating"
        :all-users="allUsers"
        submit-button-text="Create Task"
        submit-button-loading-text="Creating..."
        @submit="createTask"
        @cancel="showCreateForm = false"
      />

      <div
        v-if="showEditForm"
        class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex justify-center items-start p-8"
      >
        <div class="relative w-full max-w-2xl">
          <TaskForm
            :task-to-edit="taskToEdit"
            :all-users="allUsers"
            :is-submitting="isUpdating"
            :current-collaborators="collaboratorDetails"
            submit-button-text="Update Task"
            submit-button-loading-text="Updating..."
            @submit="updateTask"
            @cancel="closeEditModal"
          />
        </div>
      </div>

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
              <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Deadline</label>
              <select
                v-model="filters.deadline"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Deadlines</option>
                <option value="overdue">Overdue</option>
                <option value="today">Due Today</option>
                <option value="week">Due This Week</option>
                <option value="month">Due This Month</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Priority</label>
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Sort by Priority</label>
              <select
                v-model="sortBy"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="default">Default Order</option>
                <option value="priority-high">Priority (Highest First)</option>
                <option value="priority-low">Priority (Lowest First)</option>
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
              @click="fetchTasks(authStore.user.id)"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <svg
                class="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                ></path>
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
              <svg
                class="w-6 h-6 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Unassigned</p>
              <p class="text-2xl font-semibold text-gray-900">
                {{ getTaskCountByStatus('Unassigned') }}
              </p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 rounded-lg">
              <svg
                class="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Ongoing</p>
              <p class="text-2xl font-semibold text-gray-900">
                {{ getTaskCountByStatus('Ongoing') }}
              </p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <svg
                class="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Completed</p>
              <p class="text-2xl font-semibold text-gray-900">
                {{ getTaskCountByStatus('Completed') }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
        <div class="flex items-center mb-4">
          <svg
            class="w-6 h-6 text-red-600 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <h3 class="text-lg font-medium text-red-800">Backend Connection Error</h3>
        </div>
        <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
        <div class="mt-4 space-x-2">
          <button
            @click="fetchTasks"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
          >
            Try Again
          </button>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <div v-else-if="tasks.length === 0 && !error" class="text-center py-12">
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
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          ></path>
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
import TaskboardNavigation from '@/components/TaskboardNavigation.vue'

const router = useRouter()
const authStore = useAuthStore()

// Reactive data
const tasks = ref([])
const loading = ref(true)
const error = ref(null)
const role = ref(null)
const allUsers = ref([])
const collaboratorDetails = ref([])

// Form states
const showCreateForm = ref(false)
const isCreating = ref(false)
const showEditForm = ref(false)
const isUpdating = ref(false)
const taskToEdit = ref(null)

// Filters
const filters = ref({
  status: '',
  deadline: '',
  priority: '',
})

const sortBy = ref('default')

// API configuration
const KONG_API_URL = 'http://localhost:8000'

// Computed properties
const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.status) {
    filtered = filtered.filter((task) => task.status === filters.value.status)
  }

  if (filters.value.deadline && filters.value.deadline !== '') {
    const now = new Date()
    filtered = filtered.filter((task) => {
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
  // PRIORITY FILTER
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

  // ADD SORTING LOGIC HERE
  if (sortBy.value === 'priority-high') {
    filtered.sort((a, b) => {
      const priorityA = a.priority || 5
      const priorityB = b.priority || 5
      return priorityB - priorityA // Highest first (10 to 1)
    })
  } else if (sortBy.value === 'priority-low') {
    filtered.sort((a, b) => {
      const priorityA = a.priority || 5
      const priorityB = b.priority || 5
      return priorityA - priorityB // Lowest first (1 to 10)
    })
  }
  return filtered
})

// Methods
const fetchAllUsers = async () => {
  try {
    // Assume you have an endpoint that returns all users
    const response = await fetch(`${KONG_API_URL}/user`)
    if (response.ok) {
      allUsers.value = await response.json()
    } else {
      console.error('Failed to fetch all users.')
    }
  } catch (err) {
    console.error('Error fetching all users:', err)
  }
}

const fetchTasks = async (userID) => {
  try {
    loading.value = true
    error.value = null

    const queryParam = new URLSearchParams()
    if (userID) {
      queryParam.append('owner_id', userID)
    }

    const response = await fetch(
      `${KONG_API_URL}/tasks${queryParam.toString() ? `?${queryParam.toString()}` : ''}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )

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
      owner_id: authStore.currentUserId,
      priority: formData.priority,
      is_recurring: formData.is_recurring,
      recurrence_interval: formData.recurrence_interval,
      recurrence_days: formData.recurrence_days,
      recurrence_end_date: formData.recurrence_end_date,
      collaborators_to_add: formData.collaborators_to_add || [],
    }

    const response = await fetch(`${KONG_API_URL}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
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

const updateTask = async (formData) => {
  isUpdating.value = true
  try {
    const originalTask = taskToEdit.value
    const changedFields = {}

    for (const key in formData) {
      if (key === 'id') continue

      let originalValue = originalTask[key]
      let currentValue = formData[key]

      if (key === 'deadline' || key === 'recurrence_end_date') {
        originalValue = originalValue ? new Date(originalValue).toISOString().slice(0, 16) : null
        currentValue = currentValue || null
      }

      if (originalValue !== currentValue) {
        changedFields[key] = currentValue
      }
    }

    if (Object.keys(changedFields).length === 0) {
      closeEditModal()
      return // No changes to update
    }

    const payload = {
      ...changedFields,
      user_id: authStore.user.id,
    }

    const response = await fetch(`${KONG_API_URL}/tasks/${formData.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to update task')
    }

    await fetchTasks(authStore.user.id)
    closeEditModal()
  } catch (err) {
    console.error('Error updating task:', err)
    alert('Failed to update task: ' + err.message)
  } finally {
    isUpdating.value = false
  }
}

const editTask = async (task) => {
  if (authStore.user.id != task.owner_id) {
    alert('You do not have permission to edit the task.')
    return
  }
  taskToEdit.value = { ...task }
  await fetchCollaboratorsForTask(task.id)
  showEditForm.value = true
}

const closeEditModal = () => {
  showEditForm.value = false
  taskToEdit.value = null
}

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const deleteTask = async (taskId) => {
  if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
    return
  }

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
      await fetchTasks(authStore.user.id)
    } else {
      throw new Error(data.error || `Failed to delete: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting task:', err)
    alert('Failed to delete task: ' + err.message)
  }
}

const applyFilters = () => {
  // Filters are applied automatically via computed property
}

const fetchCollaboratorsForTask = async (taskId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/collaborators`)
    if (!response.ok) {
      throw new Error('Failed to fetch collaborators')
    }
    const collaborators = await response.json()

    const detailsPromises = collaborators.map((collab) =>
      fetch(`${KONG_API_URL}/user/${collab.user_id}`).then((res) => {
        if (res.ok) return res.json()
        return null
      }),
    )
    const details = (await Promise.all(detailsPromises)).filter(Boolean)

    collaboratorDetails.value = collaborators.map((collab) => {
      const userDetail = details.find((d) => d.id === collab.user_id)
      return {
        ...collab,
        name: userDetail?.name || `User ${collab.user_id}`,
        role: userDetail?.role || 'Unknown',
      }
    })
  } catch (err) {
    console.error('Error fetching collaborator details:', err)
    collaboratorDetails.value = []
    alert('Could not load collaborator details for the task.')
  }
}

const clearFilters = () => {
  filters.value.status = ''
  filters.value.deadline = ''
  filters.value.priority = ''
  sortBy.value = 'default'
}

const getTaskCountByStatus = (status) => {
  return tasks.value.filter((task) => task.status === status).length
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchTasks(authStore.user.id)
    role.value = authStore.user.role
    fetchAllUsers()
  } else {
    authStore.logout()
  }
})
</script>
