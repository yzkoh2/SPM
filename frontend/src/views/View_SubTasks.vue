<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
          <router-link
            v-if="parentTask"
            :to="`/tasks/${parentTask.id}`"
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
            Back to Task Details
          </router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">Subtasks</h1>
            <p v-if="parentTask" class="text-sm text-gray-600 mt-1">{{ parentTask.title }}</p>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
          {{ showCreateForm ? 'Cancel' : 'Create New Subtask' }}
        </button>
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
              @click="fetchSubtasks"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <TaskForm
        v-if="showCreateForm"
        title="Create New Subtask"
        :is-subtask="true"
        :is-submitting="isCreating"
        :all-users="allUsers"
        :parent-deadline="parentTask.deadline"
        submit-button-text="Create Subtask"
        submit-button-loading-text="Creating..."
        @submit="createSubtask"
        @cancel="showCreateForm = false"
      />

      <div
        v-if="showEditForm"
        class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-start justify-center"
      >
        <div class="relative w-full max-w-2xl">
          <TaskForm
            :task-to-edit="subtaskToEdit"
            :is-subtask="true"
            :is-submitting="isUpdating"
            :all-users="allUsers"
            :current-collaborators="collaboratorDetails"
            :parent-deadline="parentTask.deadline"
            submit-button-text="Update Subtask"
            submit-button-loading-text="Updating..."
            @submit="updateSubtask"
            @cancel="closeEditModal"
          />
        </div>
      </div>

      <div v-if="loading" class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p class="mt-2 text-gray-600">Loading subtasks...</p>
      </div>

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

      <div v-else-if="subtasks.length > 0" class="space-y-3">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">
              Subtasks ({{ filteredSubtasks.length
              }}{{ filteredSubtasks.length !== subtasks.length ? ` of ${subtasks.length}` : '' }})
            </h3>
            <div class="flex space-x-2">
              <span class="text-sm text-gray-500">
                {{ completedCount }}/{{ subtasks.length }} completed
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
            <div v-for="subtask in filteredSubtasks" :key="subtask.id" class="relative">
              <TaskCard
                :task="subtask"
                @view="viewSubtaskDetails"
                @edit="editSubtask"
                @delete="deleteSubtask"
              />

              <div
                v-if="updatingSubtaskId === subtask.id"
                class="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center rounded-lg"
              >
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            </div>
          </div>

          <!-- Show message if filters hide all subtasks -->
          <div v-if="filteredSubtasks.length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-600">No subtasks match the current filters.</p>
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
        <h3 class="mt-2 text-sm font-medium text-gray-900">No subtasks found</h3>
        <p class="mt-1 text-sm text-gray-500">This task doesn't have any subtasks yet.</p>
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
const updatingSubtaskId = ref(null)

// Form states
const showCreateForm = ref(false)
const isCreating = ref(false)
const showEditForm = ref(false)
const isUpdating = ref(false)
const subtaskToEdit = ref(null)
const allUsers = ref([])
const collaboratorDetails = ref([])

const filters = ref({
  status: '',
  priority: '',
})

const sortBy = ref('default')

const KONG_API_URL = 'http://localhost:8000'

// Computed properties for progress tracking
const completedCount = computed(() => {
  return subtasks.value.filter((subtask) => subtask.status === 'Completed').length
})

const progressPercentage = computed(() => {
  if (subtasks.value.length === 0) return 0
  return Math.round((completedCount.value / subtasks.value.length) * 100)
})

const filteredSubtasks = computed(() => {
  let filtered = [...subtasks.value]

  // Filter by status
  if (filters.value.status) {
    filtered = filtered.filter((subtask) => subtask.status === filters.value.status)
  }

  // Filter by priority
  if (filters.value.priority) {
    filtered = filtered.filter((subtask) => {
      const priority = subtask.priority || 5

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

// Function to fetch parent task details
async function fetchParentTask() {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
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
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Task not found')
      }
      throw new Error(`Failed to fetch subtasks: ${response.status}`)
    }

    const data = await response.json()

    subtasks.value = data.subtasks || []
  } catch (err) {
    console.error('Error fetching subtasks:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
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

// Function to create subtask
async function createSubtask(formData) {
  try {
    isCreating.value = true

    const subtaskData = {
      title: formData.title,
      description: formData.description || null,
      deadline: formData.deadline || null,
      status: formData.status,
      owner_id: authStore.currentUserId,
      parent_task_id: parentTask.value.id,
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
      body: JSON.stringify(subtaskData),
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

async function updateSubtask(formData) {
  isUpdating.value = true
  try {
    const originalSubtask = subtaskToEdit.value
    const changedFields = {}

    for (const key in formData) {
      if (key === 'id') continue

      let originalValue = originalSubtask[key]
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
      return
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
      throw new Error(errorData.error || 'Failed to update subtask')
    }

    await fetchSubtasks()
    closeEditModal()
  } catch (err) {
    console.error('Error updating subtask:', err)
    alert('Failed to update subtask: ' + err.message)
  } finally {
    isUpdating.value = false
  }
}

// Function to view subtask details
function viewSubtaskDetails(subtaskId) {
  router.push(`/tasks/${route.params.id}/subtasks/${subtaskId}?from=subtasks`)
}

// Function to edit subtask
function editSubtask(subtask) {
  if (authStore.user.id != subtask.owner_id) {
    alert('You do not have permission to edit the task.')
    return
  }
  subtaskToEdit.value = { ...subtask }
  fetchCollaboratorsForTask(subtask.id)
  showEditForm.value = true
}

function closeEditModal() {
  showEditForm.value = false
  subtaskToEdit.value = null
}

// Function to delete subtask
async function deleteSubtask(subtaskId) {
  if (!confirm('Are you sure you want to delete this subtask?')) return

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${subtaskId}`, {
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
      alert(data.message || 'Subtask deleted successfully')
      await fetchSubtasks()
    } else {
      throw new Error(data.error || `Failed to delete subtask: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting subtask:', err)
    alert('Failed to delete subtask: ' + err.message)
  }
}

// Function to get status badge color (for parent task)
function getStatusBadgeColor(status) {
  const colors = {
    Unassigned: 'bg-gray-100 text-gray-800',
    Ongoing: 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    Completed: 'bg-green-100 text-green-800',
    'On Hold': 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
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
  await fetchParentTask()
  await fetchSubtasks()
  fetchAllUsers()
})
</script>

<style scoped>
.line-through {
  text-decoration: line-through;
}
</style>
