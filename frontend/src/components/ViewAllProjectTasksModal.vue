<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-start justify-center min-h-screen px-4 pt-4 pb-20">
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <div
        class="inline-block w-full max-w-6xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-2xl rounded-2xl relative z-10"
      >
        <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-5">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-2xl font-bold text-white">All Project Tasks</h3>
              <p class="text-indigo-100 text-sm mt-1">
                View and filter all tasks in this project
              </p>
            </div>
            <button
              @click="$emit('close')"
              class="text-indigo-100 hover:text-white transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                ></path>
              </svg>
            </button>
          </div>
        </div>

        <div class="p-6 max-h-[70vh] overflow-y-auto">
          <!-- Filters -->
          <div class="mb-6 bg-gray-50 p-4 rounded-lg">
            <div class="flex flex-wrap gap-4">
              <div class="flex-1 min-w-[200px]">
                <label class="block text-sm font-medium text-gray-700 mb-1"
                  >Filter by Status</label
                >
                <select
                  v-model="filters.status"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">All Statuses</option>
                  <option value="Unassigned">Unassigned</option>
                  <option value="Ongoing">Ongoing</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <div class="flex-1 min-w-[200px]">
                <label class="block text-sm font-medium text-gray-700 mb-1"
                  >Filter by Priority</label
                >
                <select
                  v-model="filters.priority"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">All Priorities</option>
                  <option value="high">High (8-10)</option>
                  <option value="medium">Medium (4-7)</option>
                  <option value="low">Low (1-3)</option>
                </select>
              </div>

              <div class="flex-1 min-w-[200px]">
                <label class="block text-sm font-medium text-gray-700 mb-1">Sort by</label>
                <select
                  v-model="sortBy"
                  @change="applyFilters"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="default">Default Order</option>
                  <option value="deadline-earliest">Deadline (Earliest First)</option>
                  <option value="deadline-latest">Deadline (Latest First)</option>
                  <option value="priority-highest">Priority (Highest First)</option>
                  <option value="priority-lowest">Priority (Lowest First)</option>
                </select>
              </div>

              <div class="flex-1 min-w-[200px]">
                <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
                <input
                  v-model="searchTerm"
                  @input="applyFilters"
                  type="text"
                  placeholder="Search tasks..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          <!-- Task Count -->
          <div class="mb-4 text-sm text-gray-600">
            Showing <span class="font-semibold">{{ filteredTasks.length }}</span> task{{
              filteredTasks.length !== 1 ? 's' : ''
            }}
          </div>

          <!-- Tasks List -->
          <div v-if="loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p class="mt-2 text-gray-600">Loading tasks...</p>
          </div>

          <div v-else-if="filteredTasks.length === 0" class="text-center py-12 text-gray-500">
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
            <p class="mt-2 text-sm">No tasks found</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="task in filteredTasks"
              :key="task.id"
              @click="goToTask(task.id)"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer hover:border-indigo-300"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <h4 class="text-lg font-semibold text-gray-900">{{ task.title }}</h4>
                    <span
                      v-if="task.parent_task_id"
                      class="px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 rounded"
                    >
                      Subtask
                    </span>
                  </div>

                  <p v-if="task.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
                    {{ task.description }}
                  </p>

                  <div class="flex flex-wrap items-center gap-3 text-sm">
                    <span
                      :class="[
                        'px-3 py-1 rounded-full font-medium',
                        getStatusClass(task.status),
                      ]"
                    >
                      {{ task.status }}
                    </span>

                    <span
                      v-if="task.priority"
                      :class="['px-3 py-1 rounded-full font-medium', getPriorityClass(task.priority)]"
                    >
                      Priority {{ task.priority }}
                    </span>

                    <span v-if="task.deadline" class="flex items-center text-gray-600">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                        ></path>
                      </svg>
                      {{ formatDate(task.deadline) }}
                    </span>

                    <span v-if="task.owner_name" class="flex items-center text-gray-600">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        ></path>
                      </svg>
                      {{ task.owner_name }}
                    </span>
                  </div>
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
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
// import axios from 'axios' // <-- REMOVED this line

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  projectId: {
    type: Number,
    required: true,
  },
})

const emit = defineEmits(['close'])

const router = useRouter()
const tasks = ref([])
const loading = ref(false)
const filters = ref({
  status: '',
  priority: '',
})
const sortBy = ref('default')
const searchTerm = ref('')

// Fetch tasks when modal is shown
watch(
  () => props.show,
  async (newValue) => {
    if (newValue) {
      await fetchTasks()
    }
  }
)

// REPLACED axios with fetch
async function fetchTasks() {
  loading.value = true
  try {
    const response = await fetch(
      `http://localhost:8002/task-service/projects/${props.projectId}/tasks`,
      {
        credentials: 'include', // This replaces axios's withCredentials: true
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Error fetching tasks:', response.statusText, errorData)
      throw new Error(errorData.error || `Failed to fetch tasks: ${response.statusText}`)
    }

    tasks.value = await response.json()
  } catch (error) {
    console.error('Error fetching tasks:', error)
  } finally {
    loading.value = false
  }
}

const filteredTasks = computed(() => {
  let result = [...tasks.value]

  // Apply status filter
  if (filters.value.status) {
    result = result.filter((task) => task.status === filters.value.status)
  }

  // Apply priority filter
  if (filters.value.priority) {
    if (filters.value.priority === 'high') {
      result = result.filter((task) => task.priority >= 8 && task.priority <= 10)
    } else if (filters.value.priority === 'medium') {
      result = result.filter((task) => task.priority >= 4 && task.priority <= 7)
    } else if (filters.value.priority === 'low') {
      result = result.filter((task) => task.priority >= 1 && task.priority <= 3)
    }
  }

  // Apply search filter
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    result = result.filter(
      (task) =>
        task.title?.toLowerCase().includes(search) ||
        task.description?.toLowerCase().includes(search) ||
        task.owner_name?.toLowerCase().includes(search)
    )
  }

  // Apply sorting
  if (sortBy.value === 'deadline-earliest') {
    result.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(a.deadline) - new Date(b.deadline)
    })
  } else if (sortBy.value === 'deadline-latest') {
    result.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(b.deadline) - new Date(a.deadline)
    })
  } else if (sortBy.value === 'priority-highest') {
    result.sort((a, b) => (b.priority || 0) - (a.priority || 0))
  } else if (sortBy.value === 'priority-lowest') {
    result.sort((a, b) => (a.priority || 0) - (b.priority || 0))
  }

  return result
})

function applyFilters() {
  // Filters are reactive, so this is just to trigger the computed property
}

function getStatusClass(status) {
  const classes = {
    Unassigned: 'bg-gray-100 text-gray-700',
    Ongoing: 'bg-blue-100 text-blue-700',
    'Under Review': 'bg-yellow-100 text-yellow-700',
    Completed: 'bg-green-100 text-green-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

function getPriorityClass(priority) {
  if (priority >= 8) return 'bg-red-100 text-red-700'
  if (priority >= 4) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

function formatDate(dateString) {
  if (!dateString) return 'No deadline'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function goToTask(taskId) {
  emit('close')
  router.push(`/tasks/${taskId}`)
}
</script>
