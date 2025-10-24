<template>
  <div class="min-h-screen bg-gray-50">
    <EditProjectModal 
      :show="showEditModal" 
      :project="project"
      @close="showEditModal = false"
      @updated="handleProjectUpdated" />
    
    <ManageProjectTasksModal 
      :show="showManageTasksModal" 
      :project-id="parseInt(route.params.id)"
      :project-deadline="project?.deadline"
      @close="showManageTasksModal = false"
      @taskAdded="handleTaskAdded" />

    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center">
          <router-link to="/projects"
            class="flex items-center text-indigo-600 hover:text-indigo-500 text-sm font-medium">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Back to Projects
          </router-link>
          <h2 class="ml-6 text-xl font-semibold text-gray-900">Project Details</h2>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

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

      <div v-else-if="project">
        <div class="bg-white rounded-lg shadow-md p-6 mb-6 border-l-4 border-yellow-400">
          <div class="flex items-center justify-between mb-4">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ project.title }}</h1>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                  Active Project
                </span>
                <span v-if="isProjectOwner" class="flex items-center text-sm text-gray-600">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  You can edit this project
                </span>
              </div>
            </div>
            
            <div class="flex items-center space-x-3">
              <button v-if="isProjectOwner" @click="showEditModal = true"
                      class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-600 hover:bg-gray-700">
                Edit Project
              </button>
              <button @click="showManageTasksModal = true"
                      class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700">
                Manage Tasks
              </button>
              
            </div>
          </div>

          <div class="mb-6">
            <h3 class="text-sm font-semibold text-gray-700 mb-2">Description</h3>
            <p class="text-gray-700">{{ project.description || 'No description provided' }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">DEADLINE</h3>
              <p v-if="project.deadline" :class="['text-lg font-semibold', isDeadlinePassed ? 'text-red-600' : 'text-gray-900']">
                {{ formatDeadline(project.deadline) }}
              </p>
              <p v-else class="text-lg text-gray-400">No deadline set</p>
            </div>

            <div>
              <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">OWNER</h3>
              <div v-if="ownerDetails">
                <p class="text-lg font-semibold text-gray-900">{{ ownerDetails.name }}</p>
                <p class="text-sm text-gray-500">{{ ownerDetails.role }}</p>
              </div>
              <p v-else class="text-lg text-gray-400">Loading...</p>
            </div>

            <div>
              <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">PROGRESS</h3>
              <div class="flex items-center">
                <div class="flex-1">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
                         :style="{ width: `${projectProgress}%` }"></div>
                  </div>
                </div>
                <span class="ml-3 text-lg font-semibold text-gray-700">{{ projectProgress }}%</span>
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">COLLABORATORS</h3>

            <div v-if="projectCollaboratorDetails.length > 0" class="flex flex-wrap gap-2">
              <div v-for="collab in projectCollaboratorDetails" :key="collab.user_id" 
                   class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                {{ collab.name }}
              </div>
            </div>
            <p v-else class="text-sm text-gray-500">No project collaborators</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-3 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Total Tasks</p>
                <p class="text-2xl font-bold text-gray-900">{{ tasks.length }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-3 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Completed</p>
                <p class="text-2xl font-bold text-gray-900">{{ getTaskCountByStatus('Completed') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-3 bg-yellow-100 rounded-lg">
                <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">In Progress</p>
                <p class="text-2xl font-bold text-gray-900">{{ getTaskCountByStatus('Ongoing') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-3 bg-gray-100 rounded-lg">
                <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Unassigned</p>
                <p class="text-2xl font-bold text-gray-900">{{ getTaskCountByStatus('Unassigned') }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-semibold text-gray-900">Tasks ({{ filteredTasks.length }})</h3>
            <button @click="showManageTasksModal = true"
                    class="px-4 py-2 bg-indigo-600 text-white text-sm rounded-md hover:bg-indigo-700">
              View All Tasks
            </button>
          </div>

          <div class="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Status</label>
              <div class="flex flex-wrap gap-2">
                <label v-for="status in availableStatuses" :key="status" class="inline-flex items-center">
                  <input type="checkbox" :value="status" v-model="filters.statuses"
                         class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500">
                  <span class="ml-1 text-sm text-gray-700">{{ status }}</span>
                </label>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Filter by Role</label>
              <select v-model="filters.role" @change="applyFilters"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                <option value="">All Tasks</option>
                <option value="owner">My Tasks (Owner)</option>
                <option value="collaborator">Collaborating</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select v-model="filters.sortBy" @change="applyFilters"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                <option value="deadline">Deadline</option>
                <option value="title">Title</option>
                <option value="status">Status</option>
              </select>
            </div>
          </div>

          <div v-if="filteredTasks.length === 0" class="text-center py-12 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <p class="mt-2 text-sm">No tasks found</p>
          </div>

          <div v-else class="space-y-3">
            <div v-for="task in filteredTasks" :key="task.id"
  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
  @click="viewTaskDetails(task.id)">
  <div class="flex items-center space-x-4 flex-1">
    <div class="w-2 h-2 rounded-full" :class="getTaskStatusColor(task.status)"></div>
    <div class="flex-1">
      <div class="flex items-center space-x-2 mb-1">
        <h4 class="font-medium text-gray-900">{{ task.title }}</h4>
        <!-- Priority Badge -->
        <div 
          class="inline-flex items-center px-2 py-0.5 rounded-md font-bold text-xs"
          :class="getPriorityColorClass(task.priority)"
        >
          Priority: {{ task.priority || 'N/A' }}
        </div>
      </div>
      <div class="flex items-center space-x-4 mt-1 text-xs text-gray-500">
        <span v-if="task.deadline" class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z">
            </path>
          </svg>
          {{ formatDate(task.deadline) }}
        </span>
                    <span v-if="task.subtask_count > 0">📋 {{ task.subtask_count }} subtasks</span>
                    <span v-if="task.comment_count > 0">💬 {{ task.comment_count }} comments</span>
                    <span>👥 {{ task.collaborator_ids?.length || 0 }}</span>
                  </div>
                </div>
              </div>
              <span :class="['px-3 py-1 text-xs font-medium rounded-full', getStatusBadgeColor(task.status)]">
                {{ task.status }}
              </span>
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
import EditProjectModal from '@/components/EditProjectModal.vue'
import ManageProjectTasksModal from '@/components/ManageProjectTasksModal.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const KONG_API_URL = "http://localhost:8000"

// Reactive data
const loading = ref(false)
const error = ref(null)
const project = ref(null)
const tasks = ref([])
const collaborators = ref([]) // This holds the *project* collaborator IDs
const ownerDetails = ref(null)
const allUsers = ref([]) // *** NEW: Store all users here ***
const showEditModal = ref(false)
const showManageTasksModal = ref(false)

const filters = ref({
  statuses: [],
  role: '',
  sortBy: 'deadline'
})

const availableStatuses = ['Unassigned', 'Ongoing', 'Under Review', 'Completed']

// Computed properties
const getTaskCountByStatus = (status) => {
  return tasks.value.filter(task => task.status === status).length
}

const isProjectOwner = computed(() => {
  return project.value && project.value.owner_id === authStore.currentUserId
})

const projectProgress = computed(() => {
  if (tasks.value.length === 0) return 0
  const completed = getTaskCountByStatus('Completed')
  return Math.round((completed / tasks.value.length) * 100)
})

const isDeadlinePassed = computed(() => {
  if (!project.value?.deadline) return false
  return new Date(project.value.deadline) < new Date()
})

// *** NEW: Correctly find project collaborators ***
const projectCollaboratorDetails = computed(() => {
  if (!collaborators.value || allUsers.value.length === 0) {
    return []
  }
  // Map the IDs from collaborators.value to the full user objects
  return collaborators.value.map(id => {
    const user = allUsers.value.find(u => u.id === id)
    return {
      user_id: id,
      name: user?.name || `User ${id}`,
      role: user?.role || 'N/A'
    }
  })
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.statuses.length > 0) {
    filtered = filtered.filter(task => filters.value.statuses.includes(task.status))
  }

  if (filters.value.role === 'owner') {
    filtered = filtered.filter(task => task.owner_id === authStore.currentUserId)
  } else if (filters.value.role === 'collaborator') {
    filtered = filtered.filter(task => 
      task.collaborator_ids && task.collaborator_ids.includes(authStore.currentUserId)
    )
  }

  filtered.sort((a, b) => {
    switch (filters.value.sortBy) {
      case 'deadline':
        return new Date(a.deadline || '9999-12-31') - new Date(b.deadline || '9999-12-31')
      case 'title':
        return a.title.localeCompare(b.title)
      case 'status':
        return a.status.localeCompare(b.status)
      default:
        return 0
    }
  })

  return filtered
})

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

const getStatusDotColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-400',
    'Ongoing': 'bg-yellow-400',
    'Under Review': 'bg-orange-400',
    'Completed': 'bg-green-400'
  }
  return colors[status] || 'bg-gray-400'
}

const formatDeadline = (dateString) => {
  if (!dateString) return 'No deadline'
  const date = new Date(dateString)
  const options = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }
  return date.toLocaleDateString('en-US', options)
}

const formatTaskDate = (dateString) => {
  if (!dateString) return 'No date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// API calls

// *** NEW: Fetch ALL users once ***
const fetchAllUsers = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/user`)
    if (response.ok) {
      allUsers.value = await response.json()
    } else {
      console.warn(`Failed to load all users`)
      allUsers.value = []
    }
  } catch (err) {
    console.error(`Error fetching all users:`, err)
    allUsers.value = []
  }
}

// *** REMOVED fetchUserDetails and fetchAllCollaborators ***

const loadDashboard = async () => {
  try {
    loading.value = true
    error.value = null

    const projectId = route.params.id
    const userId = authStore.currentUserId

    // *** MODIFIED: Fetch all users FIRST ***
    await fetchAllUsers()

    // Fetch Project
    const projectResponse = await fetch(`${KONG_API_URL}/projects/${projectId}?user_id=${userId}`)
    if (!projectResponse.ok) {
      const errorData = await projectResponse.json()
      throw new Error(errorData.error || 'Failed to load project')
    }
    const projectData = await projectResponse.json()
    
    project.value = projectData.project || projectData

    // *** MODIFIED: Set owner details synchronously ***
    if (project.value.owner_id) {
      const owner = allUsers.value.find(u => u.id === project.value.owner_id)
      ownerDetails.value = owner || { name: `User ${project.value.owner_id}`, role: 'Unknown' }
    }

    // Fetch Dashboard (Tasks & Collaborator IDs)
    const tasksResponse = await fetch(`${KONG_API_URL}/projects/${projectId}/dashboard?user_id=${userId}`)
    if (tasksResponse.ok) {
      const dashboardData = await tasksResponse.json()
      tasks.value = dashboardData.tasks || []
      // This correctly assigns the array of IDs [1, 2, 3]
      collaborators.value = dashboardData.collaborators || []
    } else {
      tasks.value = []
      collaborators.value = []
    }
    
    // *** REMOVED: await fetchAllCollaborators() ***
    // The new computed property 'projectCollaboratorDetails' handles this.

  } catch (err) {
    console.error('Error loading dashboard:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}?fromProject=${route.params.id}`)
}

const applyFilters = () => {
  // Filters are reactive
}


const handleProjectUpdated = () => {
  loadDashboard()
}

const handleTaskAdded = () => {
  loadDashboard()
}

const getPriorityColorClass = (priority) => {
  if (!priority) return 'bg-gray-100 text-gray-700 border border-gray-300';
  
  if (priority >= 8 && priority <= 10) {
    return 'bg-red-100 text-red-800 border border-red-300';
  } else if (priority >= 4 && priority <= 7) {
    return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
  } else if (priority >= 1 && priority <= 3) {
    return 'bg-green-100 text-green-800 border border-green-300';
  }
  return 'bg-gray-100 text-gray-700 border border-gray-300';
};

const getTaskStatusColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-400',
    'Ongoing': 'bg-yellow-400',
    'Under Review': 'bg-orange-400',
    'Completed': 'bg-green-400'
  }
  return colors[status] || 'bg-gray-400'
}

const formatDate = (dateString) => {
  if (!dateString) return 'No deadline';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};



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