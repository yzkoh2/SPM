<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay with animation -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 backdrop-blur-sm" @click="$emit('close')"></div>

      <!-- Modal panel -->
      <div class="inline-block w-full max-w-3xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-2xl rounded-2xl relative z-10">
        
        <!-- Header -->
        <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-5">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-2xl font-bold text-white">Manage Project Tasks</h3>
              <p class="text-indigo-100 text-sm mt-1">Create new tasks or add existing ones to this project</p>
            </div>
            <button @click="$emit('close')" class="text-indigo-100 hover:text-white transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content Area -->
        <div class="p-6">
          <!-- Error Display -->
          <div v-if="error" class="mb-4 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-red-700 font-medium">{{ error }}</p>
            </div>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="mb-4 p-4 bg-green-50 border-l-4 border-green-400 rounded-r-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <p class="text-sm text-green-700 font-medium">{{ successMessage }}</p>
            </div>
          </div>

          <!-- Tabs -->
          <div class="border-b border-gray-200 mb-6">
            <nav class="-mb-px flex space-x-8">
              <button @click="activeTab = 'create'"
                      :class="[activeTab === 'create' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-semibold text-sm transition-colors flex items-center']">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Create New Task
              </button>
              <button @click="activeTab = 'add'"
                      :class="[activeTab === 'add' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-semibold text-sm transition-colors flex items-center']">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Add Existing Task
              </button>
            </nav>
          </div>

          <!-- Create New Task Tab -->
          <div v-if="activeTab === 'create'">
            <form @submit.prevent="createTask" class="space-y-6">
              
              <!-- Task Title -->
              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  Task Title
                  <span class="text-red-500 ml-1">*</span>
                </label>
                <input v-model="newTask.title" 
                       type="text" 
                       required
                       placeholder="Enter a clear, descriptive task title"
                       class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all">
              </div>

              <!-- Description -->
              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"></path>
                  </svg>
                  Description
                </label>
                <textarea v-model="newTask.description" 
                          rows="4"
                          placeholder="Provide additional details about this task..."
                          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"></textarea>
                <p class="text-xs text-gray-500 mt-1">Optional: Add any relevant details or context</p>
              </div>

              <!-- Deadline and Status Row -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Deadline -->
                <div>
                  <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    Deadline
                  </label>
                  <input v-model="newTask.deadline" 
                         type="datetime-local"
                         class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all">
                </div>

                <!-- Status -->
                <div>
                  <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                    <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Status
                  </label>
                  <select v-model="newTask.status"
                          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white">
                    <option value="Unassigned">Unassigned</option>
                    <option value="Ongoing">Ongoing</option>
                    <option value="Under Review">Under Review</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
              </div>

              <!-- Priority -->
              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                  </svg>
                  Priority (1-10)
                </label>
                <div class="flex items-center space-x-4">
                  <input v-model.number="newTask.priority" 
                         type="range" 
                         min="1" 
                         max="10"
                         class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                  <span class="flex items-center justify-center w-12 h-12 text-lg font-bold text-white bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg shadow-md">
                    {{ newTask.priority }}
                  </span>
                </div>
                <div class="flex justify-between text-xs text-gray-500 mt-2">
                  <span>Low</span>
                  <span>Medium</span>
                  <span>High</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button type="button" 
                        @click="$emit('close')"
                        class="px-6 py-3 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
                <button type="submit" 
                        :disabled="creating"
                        class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg text-sm font-semibold hover:from-indigo-700 hover:to-indigo-800 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center">
                  <svg v-if="!creating" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  <svg v-else class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ creating ? 'Creating...' : 'Create Task' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Add Existing Task Tab -->
          <div v-if="activeTab === 'add'">
            <div class="space-y-4">
              <!-- Loading -->
              <div v-if="loadingStandaloneTasks" class="text-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                <p class="text-sm text-gray-500 mt-4">Loading your tasks...</p>
              </div>

              <!-- Standalone Tasks List -->
              <div v-else-if="standaloneTasks.length > 0" class="space-y-3 max-h-96 overflow-y-auto pr-2">
                <div v-for="task in standaloneTasks" :key="task.id"
                     class="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-xl p-5 hover:border-indigo-400 hover:shadow-md transition-all">
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      <h4 class="font-semibold text-gray-900 text-lg">{{ task.title }}</h4>
                      <p v-if="task.description" class="text-sm text-gray-600 mt-2 line-clamp-2">{{ task.description }}</p>
                      <div class="flex items-center space-x-4 mt-3">
                        <span :class="['px-3 py-1 rounded-full text-xs font-semibold', getStatusColor(task.status)]">
                          {{ task.status }}
                        </span>
                        <span v-if="task.deadline" class="text-xs text-gray-500 flex items-center">
                          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                          </svg>
                          {{ formatDate(task.deadline) }}
                        </span>
                      </div>
                    </div>
                    <button @click="addTaskToProject(task.id)" 
                            :disabled="addingTask === task.id"
                            class="ml-4 px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-sm font-semibold rounded-lg hover:from-indigo-700 hover:to-indigo-800 disabled:from-gray-400 disabled:to-gray-400 transition-all shadow-md hover:shadow-lg flex items-center whitespace-nowrap">
                      <svg v-if="!addingTask" class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                      </svg>
                      {{ addingTask === task.id ? 'Adding...' : 'Add to Project' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- No Tasks -->
              <div v-else class="text-center py-16">
                <div class="bg-gray-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                  <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">No standalone tasks</h3>
                <p class="text-sm text-gray-500 mb-6">All your tasks are already assigned to projects.</p>
                <button @click="activeTab = 'create'" class="text-indigo-600 hover:text-indigo-700 font-medium text-sm flex items-center mx-auto">
                  <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Create a new task instead
                </button>
              </div>
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
    
    // Reset form
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

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>