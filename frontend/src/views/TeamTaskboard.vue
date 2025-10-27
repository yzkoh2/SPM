<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Team Taskboard</h1>
        <p class="text-sm text-gray-600 mt-1">View and manage tasks for all members of your team</p>
      </div>

      <TaskboardNavigation />

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3 class="text-lg font-medium text-red-800">Error Loading Team Tasks</h3>
        </div>
        <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
        <div class="mt-4">
          <button @click="loadTeamTasks" 
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors">
            Try Again
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="tasks.length === 0 && !error" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z">
          </path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No team tasks found</h3>
        <p class="mt-1 text-sm text-gray-500">Your team members haven't created any tasks yet.</p>
      </div>

      <!-- Task Dashboard -->
      <div v-else>
        <!-- Filters and Sorting Section -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
              <!-- Filter by Team Member -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Team Member</label>
                <select v-model="filters.teamMember" @change="applyFilters"
                  class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">All Team Members</option>
                  <option v-for="member in teamMembers" :key="member.id" :value="member.id">
                    {{ member.name }}
                  </option>
                </select>
              </div>

              <!-- Filter by Status -->
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

              <!-- Filter by Priority -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Priority</label>
                <select v-model="filters.priority" @change="applyFilters"
                  class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">All Priorities</option>
                  <option value="high">High (8-10)</option>
                  <option value="medium">Medium (4-7)</option>
                  <option value="low">Low (1-3)</option>
                </select>
              </div>             

              <!-- Sort by Deadline -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Sort by Deadline</label>
                <select v-model="sortBy" @change="applyFilters"
                  class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="default">Default Order</option>
                  <option value="deadline-asc">Deadline (Earliest First)</option>
                  <option value="deadline-desc">Deadline (Latest First)</option>
                </select>
              </div>
            

              <!-- Sort by Priority -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Sort by Priority</label>
                <select v-model="prioritySort" @change="applyFilters"
                  class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="default">Default Order</option>
                  <option value="priority-high">Highest First</option>
                  <option value="priority-low">Lowest First</option>
                </select>
              </div>
            </div>

            <div class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
              <button @click="clearFilters"
                class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors">
                Clear Filters
              </button>
              <button @click="loadTeamTasks"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors">
                Refresh
              </button>
            </div>
          </div>
        </div>

        <!-- Status Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2">
                  </path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Total Tasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ filteredAndSortedTasks.length }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-gray-100 rounded-lg">
                <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                  </path>
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Completed</p>
                <p class="text-2xl font-semibold text-gray-900">{{ getTaskCountByStatus('Completed') }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Task Cards Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <TaskCard v-for="task in filteredAndSortedTasks" :key="task.id" :task="task" @view="viewTaskDetails" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TaskboardNavigation from '@/components/TaskboardNavigation.vue'
import TaskCard from '@/components/TaskCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const KONG_API_URL = "http://localhost:8000"

// Reactive state
const tasks = ref([])
const teamMembers = ref([])
const teamMemberIds = ref([])
const loading = ref(false)
const error = ref(null)

// Filters
const filters = ref({
  teamMember: '',
  status: '',
  priority: ''
})

const sortBy = ref('default')
const prioritySort = ref('default')  // For priority sorting

// Computed properties
const filteredAndSortedTasks = computed(() => {
  let filtered = [...tasks.value]

  
  if (filters.value.teamMember) {
    const memberId = parseInt(filters.value.teamMember)
    filtered = filtered.filter(task => {
      
      if (task.owner_id === memberId) return true
      
      
      if (task.collaborator_ids && task.collaborator_ids.includes(memberId)) return true
      
      return false
    })
  }

  
  if (filters.value.status) {
    filtered = filtered.filter(task => task.status === filters.value.status)
  }
// Filter by priority
  if (filters.value.priority) {
    filtered = filtered.filter(task => {
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
  
  if (sortBy.value === 'deadline-asc') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(a.deadline) - new Date(b.deadline)
    })
  } else if (sortBy.value === 'deadline-desc') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(b.deadline) - new Date(a.deadline)
    })
  }

  // Apply priority sorting
  else if (prioritySort.value === 'priority-high') {
    filtered.sort((a, b) => {
      const priorityA = a.priority || 5
      const priorityB = b.priority || 5
      return priorityB - priorityA
    })
  } else if (prioritySort.value === 'priority-low') {
    filtered.sort((a, b) => {
      const priorityA = a.priority || 5
      const priorityB = b.priority || 5
      return priorityA - priorityB
    })
  }

  return filtered
})


const getTaskCountByStatus = (status) => {
  return filteredAndSortedTasks.value.filter(task => task.status === status).length
}

const applyFilters = () => {
  
}

const clearFilters = () => {
  filters.value.teamMember = ''
  filters.value.status = ''
  filters.value.priority = ''
  sortBy.value = 'default'
  prioritySort.value = 'default'
}

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const getTeamMemberIds = async (teamId) => {
  const response = await fetch(`${KONG_API_URL}/user/team/${teamId}`)
  if (!response.ok) throw new Error('Failed to fetch team members')

  const members = await response.json()
  teamMembers.value = members
  return members.map(member => member.id)
}

const fetchCollaboratorsForTask = async (taskId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/collaborators`)
    if (response.ok) {
      const collaborators = await response.json()
      return collaborators.map(c => c.user_id)
    }
    return []
  } catch (err) {
    console.error(`Error fetching collaborators for task ${taskId}:`, err)
    return []
  }
}

const loadTeamTasks = async () => {
  loading.value = true
  error.value = null

  try {
    const userId = authStore.user.id

    
    const userResponse = await fetch(`${KONG_API_URL}/user/${userId}`)
    if (!userResponse.ok) throw new Error('Failed to fetch user data')
    const userData = await userResponse.json()

    const teamId = userData.team_id
    if (!teamId) {
      tasks.value = []
      error.value = 'You are not assigned to a team'
      return
    }

    
    const memberIds = await getTeamMemberIds(teamId)
    teamMemberIds.value = memberIds

    if (memberIds.length === 0) {
      tasks.value = []
      return
    }

    
    const taskPromises = memberIds.map(memberId =>
      fetch(`${KONG_API_URL}/tasks?owner_id=${memberId}`)
        .then(res => res.ok ? res.json() : [])
        .catch(() => [])
    )

    const ownedTasksArrays = await Promise.all(taskPromises)
    const ownedTasks = ownedTasksArrays.flat()

    
    const taskMap = new Map()
    ownedTasks.forEach(task => {
      taskMap.set(task.id, { ...task, collaborator_ids: [] })
    })

    
    const collaboratorPromises = Array.from(taskMap.keys()).map(async (taskId) => {
      const collaboratorIds = await fetchCollaboratorsForTask(taskId)
      return { taskId, collaboratorIds }
    })

    const collaboratorResults = await Promise.all(collaboratorPromises)

    
    collaboratorResults.forEach(({ taskId, collaboratorIds }) => {
      if (taskMap.has(taskId)) {
        taskMap.get(taskId).collaborator_ids = collaboratorIds
        
       
        const hasTeamCollaborator = collaboratorIds.some(collabId => 
          memberIds.includes(collabId)
        )
        
    
        if (hasTeamCollaborator) {
          taskMap.get(taskId).has_team_collaborator = true
        }
      }
    })


    const relevantTasks = Array.from(taskMap.values()).filter(task => {
      
      return memberIds.includes(task.owner_id) || task.has_team_collaborator
    })

    tasks.value = relevantTasks

  } catch (err) {
    console.error('Error fetching team tasks:', err)
    error.value = err.message
    tasks.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTeamTasks()
})
</script>