<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="$emit('close')"></div>

      <!-- Modal panel -->
      <div class="inline-block w-full max-w-3xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900">Manage Project Tasks</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-700">{{ successMessage }}</p>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200 mb-6">
          <nav class="-mb-px flex space-x-8">
            <button @click="activeTab = 'create'"
                    :class="[activeTab === 'create' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
              Create New Task
            </button>
            <button @click="activeTab = 'add'"
                    :class="[activeTab === 'add' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
              Add Existing Task
            </button>
          </nav>
        </div>

        <!-- Create New Task Tab -->
        <div v-if="activeTab === 'create'">
          <form @submit.prevent="createTask">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Task Title *</label>
                <input v-model="newTask.title" type="text" required
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea v-model="newTask.description" rows="3"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"></textarea>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
                  <input v-model="newTask.deadline" type="datetime-local"
                         class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select v-model="newTask.status"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                    <option value="Unassigned">Unassigned</option>
                    <option value="Ongoing">Ongoing</option>
                    <option value="Under Review">Under Review</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Priority (1-10)</label>
                <input v-model.number="newTask.priority" type="number" min="1" max="10"
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
              </div>
            </div>

            <div class="mt-6 flex justify-end space-x-3">
              <button type="button" @click="$emit('close')"
                      class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" :disabled="creating"
                      class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400">
                {{ creating ? 'Creating...' : 'Create Task' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Add Existing Task Tab -->
        <div v-if="activeTab === 'add'">
          <div class="space-y-4">
            <!-- Loading -->
            <div v-if="loadingStandaloneTasks" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
              <p class="text-sm text-gray-500 mt-2">Loading your tasks...</p>
            </div>

            <!-- Standalone Tasks List -->
            <div v-else-if="standaloneTasks.length > 0" class="space-y-2 max-h-96 overflow-y-auto">
              <div v-for="task in standaloneTasks" :key="task.id"
                   class="border border-gray-200 rounded-lg p-4 hover:border-indigo-500 transition-colors">
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ task.title }}</h4>
                    <p v-if="task.description" class="text-sm text-gray-600 mt-1">{{ task.description }}</p>
                    <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span :class="['px-2 py-1 rounded-full', getStatusColor(task.status)]">{{ task.status }}</span>
                      <span v-if="task.deadline">Due: {{ formatDate(task.deadline) }}</span>
                    </div>
                  </div>
                  <button @click="addTaskToProject(task.id)" 
                          :disabled="addingTask === task.id"
                          class="ml-4 px-3 py-1 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700 disabled:bg-gray-400">
                    {{ addingTask === task.id ? 'Adding...' : 'Add to Project' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- No Tasks -->
            <div v-else class="text-center py-12">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
              <h3 class="mt-2 text-sm font-medium text-gray-900">No standalone tasks</h3>
              <p class="mt-1 text-sm text-gray-500">All your tasks are already assigned to projects.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: Boolean,
  projectId: Number
})

const emit = defineEmits(['close', 'taskAdded'])

const authStore = useAuthStore()
const KONG_API_URL = "http://localhost:8000"

const activeTab = ref('create')
const creating = ref(false)
const addingTask = ref(null)
const loadingStandaloneTasks = ref(false)
const error = ref(null)
const successMessage = ref(null)

const newTask = ref({
  title: '',
  description: '',
  deadline: '',
  status: 'Unassigned',
  priority: 5
})

const standaloneTasks = ref([])

// Watch for modal open
watch(() => props.show, (isOpen) => {
  if (isOpen && activeTab.value === 'add') {
    loadStandaloneTasks()
  }
})

// Watch for tab change
watch(activeTab, (newTab) => {
  if (newTab === 'add' && props.show) {
    loadStandaloneTasks()
  }
})

const createTask = async () => {
  try {
    creating.value = true
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/projects/${props.projectId}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...newTask.value,
        owner_id: authStore.currentUserId,
        user_id: authStore.currentUserId
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to create task')
    }

    successMessage.value = 'Task created successfully!'
    newTask.value = {
      title: '',
      description: '',
      deadline: '',
      status: 'Unassigned',
      priority: 5
    }

    setTimeout(() => {
      emit('taskAdded')
      emit('close')
    }, 1000)

  } catch (err) {
    console.error('Error creating task:', err)
    error.value = err.message
  } finally {
    creating.value = false
  }
}

const loadStandaloneTasks = async () => {
  try {
    loadingStandaloneTasks.value = true
    error.value = null

    const response = await fetch(`${KONG_API_URL}/tasks/standalone?user_id=${authStore.currentUserId}`)

    if (!response.ok) {
      throw new Error('Failed to load tasks')
    }

    standaloneTasks.value = await response.json()

  } catch (err) {
    console.error('Error loading standalone tasks:', err)
    error.value = err.message
  } finally {
    loadingStandaloneTasks.value = false
  }
}

const addTaskToProject = async (taskId) => {
  try {
    addingTask.value = taskId
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/add-to-project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_id: props.projectId,
        user_id: authStore.currentUserId
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add task to project')
    }

    successMessage.value = 'Task added to project!'
    standaloneTasks.value = standaloneTasks.value.filter(t => t.id !== taskId)

    setTimeout(() => {
      emit('taskAdded')
      if (standaloneTasks.value.length === 0) {
        emit('close')
      }
    }, 1000)

  } catch (err) {
    console.error('Error adding task to project:', err)
    error.value = err.message
  } finally {
    addingTask.value = null
  }
}

const getStatusColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-blue-100 text-blue-800',
    'Under Review': 'bg-yellow-100 text-yellow-800',
    'Completed': 'bg-green-100 text-green-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>