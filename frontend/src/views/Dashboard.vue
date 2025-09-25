<template>
    <div class="min-h-screen bg-gray-50">
      <!-- Header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center py-6">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Task Dashboard</h1>
              <p class="text-sm text-gray-600 mt-1">Manage your tasks and collaborate with your team</p>
            </div>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-500">Welcome back!</span>
              <button @click="logout" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>
  
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
        <div v-if="showCreateForm" class="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Create New Task</h2>
          <form @submit.prevent="createTask" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Task Title</label>
                <input v-model="newTask.title" type="text" required 
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
                <input v-model="newTask.deadline" type="datetime-local"
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea v-model="newTask.description" rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="Describe the task in detail..."></textarea>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select v-model="newTask.status" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                  <option value="unassigned">Unassigned</option>
                  <option value="ongoing">Ongoing</option>
                  <option value="under_review">Under Review</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Assign To (Optional)</label>
                <input v-model="newTask.assigned_to" type="number" placeholder="User ID"
                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
              </div>
            </div>
            
            <div class="flex justify-end space-x-3">
              <button type="button" @click="showCreateForm = false" 
                      class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors">
                Cancel
              </button>
              <button type="submit" :disabled="isCreating"
                      class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors disabled:opacity-50">
                {{ isCreating ? 'Creating...' : 'Create Task' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Dashboard Tabs -->
        <div class="bg-white rounded-lg shadow-md mb-6">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8 px-6 py-3" aria-label="Tabs">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                @click="activeTab = tab.key"
                :class="[
                  activeTab === tab.key
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
                ]"
              >
                {{ tab.label }}
                <span v-if="taskCounts[tab.key] !== undefined" 
                      class="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2.5 rounded-full text-xs font-medium">
                  {{ taskCounts[tab.key] }}
                </span>
              </button>
            </nav>
          </div>
          
          <!-- Filters -->
          <div class="p-6 border-b border-gray-100">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
              <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Status</label>
                  <select v-model="filters.status" @change="applyFilters"
                          class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">All Statuses</option>
                    <option value="unassigned">Unassigned</option>
                    <option value="ongoing">Ongoing</option>
                    <option value="under_review">Under Review</option>
                    <option value="completed">Completed</option>
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
                <button @click="fetchUserTasks" 
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors">
                  Refresh
                </button>
              </div>
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
                <p class="text-2xl font-semibold text-gray-900">{{ currentTasks.length }}</p>
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
                <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('unassigned') }}</p>
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
                <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('ongoing') }}</p>
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
                <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('completed') }}</p>
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
            <button @click="fetchUserTasks" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md">
              Try Again
            </button>
          </div>
        </div>
  
        <!-- Tasks Grid -->
        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
        
        <div v-else-if="currentTasks.length === 0 && !error" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No tasks found</h3>
          <p class="mt-1 text-sm text-gray-500">{{ getEmptyStateMessage() }}</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="task in filteredTasks" :key="task.id" 
               class="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border-l-4 cursor-pointer transform hover:-translate-y-1"
               :class="getStatusBorderColor(task.status)"
               @click="viewTaskDetails(task.id)">
            
            <div class="p-6">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors">
                    {{ task.title }}
                  </h3>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getStatusBadgeColor(task.status)">
                    {{ formatStatus(task.status) }}
                  </span>
                </div>
                
                <div class="flex items-center space-x-2 ml-4">
                  <button @click.stop="showAssignmentDialog(task)" 
                          class="text-gray-400 hover:text-indigo-600 transition-colors p-1 rounded hover:bg-gray-100"
                          title="Assign Task">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                  </button>
                  <button @click.stop="deleteTask(task.id)" 
                          class="text-gray-400 hover:text-red-600 transition-colors p-1 rounded hover:bg-red-50"
                          title="Delete Task">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </div>
              
              <p class="text-sm text-gray-600 mt-3 line-clamp-2">
                {{ task.description || 'No description available' }}
              </p>
              
              <!-- NEW: Progress bar for subtasks -->
              <div v-if="task.subtask_count > 0" class="mt-4">
                <div class="flex items-center justify-between text-sm text-gray-600 mb-1">
                  <span>Progress: {{ task.completion_percentage || 0 }}%</span>
                  <span>{{ task.subtask_count }} subtasks</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-green-600 h-2 rounded-full transition-all duration-300" 
                    :style="{ width: (task.completion_percentage || 0) + '%' }"
                  ></div>
                </div>
              </div>
              
              <div v-if="task.deadline" class="flex items-center mt-4 text-sm">
                <svg class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
                </svg>
                <span :class="getDeadlineColor(task.deadline)">
                  Due: {{ formatDeadline(task.deadline) }}
                </span>
              </div>
              
              <!-- NEW: Ownership and assignment info -->
              <div class="mt-4 pt-4 border-t border-gray-100">
                <div class="flex items-center justify-between text-xs text-gray-600">
                  <div class="flex items-center space-x-4">
                    <span>Owner: {{ task.owner_id }}</span>
                    <span v-if="task.assigned_to">
                      Assigned: {{ task.assigned_to }}
                    </span>
                    <span v-else class="text-orange-600">
                      Unassigned
                    </span>
                  </div>
                  <span class="text-indigo-500">Click to view →</span>
                </div>
              </div>
              
              <div class="mt-2 grid grid-cols-3 gap-2 text-xs text-gray-600">
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  {{ task.subtask_count || 0 }} subtasks
                </div>
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                  </svg>
                  {{ task.comment_count || 0 }} comments
                </div>
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                  </svg>
                  {{ task.attachment_count || 0 }} files
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Assignment Dialog -->
        <div v-if="showAssignDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
              {{ selectedTask?.assigned_to ? 'Reassign Task' : 'Assign Task' }}
            </h3>
            <p class="text-sm text-gray-600 mb-4">Task: "{{ selectedTask?.title }}"</p>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ selectedTask?.assigned_to ? 'Reassign to User ID:' : 'Assign to User ID:' }}
                </label>
                <input 
                  v-model="assignmentUserId" 
                  type="number" 
                  placeholder="Enter user ID"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
              </div>
              
              <div class="flex items-center space-x-2">
                <input 
                  v-model="transferOwnership" 
                  type="checkbox" 
                  id="transferOwnership"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                <label for="transferOwnership" class="text-sm text-gray-700">
                  Transfer ownership (assignment automatically transfers ownership)
                </label>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="cancelAssignment" 
                      class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors">
                Cancel
              </button>
              <button @click="confirmAssignment" :disabled="!assignmentUserId"
                      class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors disabled:opacity-50">
                {{ selectedTask?.assigned_to ? 'Reassign' : 'Assign' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  
  // Reactive data
  const userTasks = ref({
    owned: [],
    assigned: [],
    created: [],
    unassigned_owned: []
  })
  const loading = ref(true)
  const showCreateForm = ref(false)
  const isCreating = ref(false)
  const error = ref(null)
  const activeTab = ref('assigned')
  
  // Assignment dialog
  const showAssignDialog = ref(false)
  const selectedTask = ref(null)
  const assignmentUserId = ref('')
  const transferOwnership = ref(true)
  
  // New task form data  
  const newTask = ref({
    title: '',
    deadline: '',
    description: '',
    status: 'unassigned',
    assigned_to: null
  })
  
  // Filters
  const filters = ref({
    status: '',
    deadline: ''
  })
  
  // Tab configuration
  const tabs = ref([
    { key: 'assigned', label: 'Assigned to Me' },
    { key: 'owned', label: 'I Own' },
    { key: 'unassigned_owned', label: 'Unassigned (Mine)' },
    { key: 'created', label: 'I Created' }
  ])
  
  // API configuration
  const KONG_API_URL = "http://localhost:8000"
  const currentUserId = 1
  
  // Computed properties
  const taskCounts = computed(() => {
    return {
      assigned: userTasks.value.assigned?.length || 0,
      owned: userTasks.value.owned?.length || 0,
      unassigned_owned: userTasks.value.unassigned_owned?.length || 0,
      created: userTasks.value.created?.length || 0
    }
  })
  
  const currentTasks = computed(() => {
    return userTasks.value[activeTab.value] || []
  })
  
  const filteredTasks = computed(() => {
    let filtered = [...currentTasks.value]
    
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
  const fetchUserTasks = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await fetch(`${KONG_API_URL}/users/${currentUserId}/tasks?include_owned=true&include_assigned=true&include_created=true&include_unassigned=true`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        userTasks.value = await response.json()
      } else {
        const errorText = await response.text()
        throw new Error(`API Error: ${response.status} - ${errorText}`)
      }
    } catch (err) {
      console.error('Error fetching user tasks:', err)
      error.value = `Failed to fetch tasks: ${err.message}`
      userTasks.value = { owned: [], assigned: [], created: [], unassigned_owned: [] }
    } finally {
      loading.value = false
    }
  }
  
  const createTask = async () => {
    try {
      isCreating.value = true
      error.value = null
      
      const taskData = {
        title: newTask.value.title,
        description: newTask.value.description || null,
        deadline: newTask.value.deadline || null,
        status: newTask.value.status,
        created_by: currentUserId,
        assigned_to: newTask.value.assigned_to || null
      }
      
      const response = await fetch(`${KONG_API_URL}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskData)
      })
      
      if (response.ok) {
        await fetchUserTasks()
        
        newTask.value = {
          title: '',
          deadline: '',
          description: '',
          status: 'unassigned',
          assigned_to: null
        }
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
  
  const showAssignmentDialog = (task) => {
    selectedTask.value = task
    assignmentUserId.value = task.assigned_to || ''
    showAssignDialog.value = true
  }
  
  const confirmAssignment = async () => {
    if (!assignmentUserId.value || !selectedTask.value) return
    
    try {
      const response = await fetch(`${KONG_API_URL}/tasks/${selectedTask.value.id}/assign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          assigned_to: parseInt(assignmentUserId.value),
          updated_by: currentUserId
        })
      })
      
      if (response.ok) {
        await fetchUserTasks()
        cancelAssignment()
        alert('Task assigned successfully!')
      } else {
        throw new Error(`Failed to assign task: ${response.status}`)
      }
    } catch (err) {
      console.error('Error assigning task:', err)
      alert('Failed to assign task: ' + err.message)
    }
  }
  
  const cancelAssignment = () => {
    showAssignDialog.value = false
    selectedTask.value = null
    assignmentUserId.value = ''
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
        await fetchUserTasks()
      } else {
        throw new Error(`Failed to delete task: ${response.status}`)
      }
    } catch (err) {
      console.error('Error deleting task:', err)
      alert('Failed to delete task: ' + err.message)
    }
  }
  
  const applyFilters = () => {
    // Filters are applied automatically via computed property
  }
  
  const clearFilters = () => {
    filters.value.status = ''
    filters.value.deadline = ''
  }
  
  const getTaskCountByStatus = (status) => {
    return currentTasks.value.filter(task => task.status === status).length
  }
  
  const getStatusBorderColor = (status) => {
    const colors = {
      'unassigned': 'border-gray-400',
      'ongoing': 'border-yellow-400',
      'under_review': 'border-orange-400',
      'completed': 'border-green-400'
    }
    return colors[status] || 'border-gray-400'
  }
  
  const getStatusBadgeColor = (status) => {
    const colors = {
      'unassigned': 'bg-gray-100 text-gray-800',
      'ongoing': 'bg-yellow-100 text-yellow-800',
      'under_review': 'bg-orange-100 text-orange-800',
      'completed': 'bg-green-100 text-green-800'
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
    if (!deadline) return 'No deadline set'
    const date = new Date(deadline)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
  
  const formatStatus = (status) => {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }
  
  const getEmptyStateMessage = () => {
    const messages = {
      assigned: 'No tasks assigned to you yet.',
      owned: 'You don\'t own any tasks yet.',
      unassigned_owned: 'All your tasks are assigned.',
      created: 'You haven\'t created any tasks yet.'
    }
    return messages[activeTab.value] || 'No tasks found.'
  }
  
  const logout = () => {
    localStorage.removeItem('authToken')
    router.push('/login')
  }
  
  onMounted(() => {
    fetchUserTasks()
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