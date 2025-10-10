<template>
    <div class="min-h-screen bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Department Taskboard</h1>
          <p class="text-sm text-gray-600 mt-1">View and manage tasks across your entire department</p>
        </div>
  
        <TaskboardNavigation />
  
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
          <div class="flex items-center mb-4">
            <svg class="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <h3 class="text-lg font-medium text-red-800">Error Loading Department Tasks</h3>
          </div>
          <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
          <div class="mt-4">
            <button @click="fetchDepartmentTasks" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md">
              Try Again
            </button>
          </div>
        </div>
  
        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
  
        <div v-else-if="tasks.length === 0 && !error" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4">
            </path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No department tasks found</h3>
          <p class="mt-1 text-sm text-gray-500">Your department members haven't created any tasks yet.</p>
        </div>
  
        <div v-else>
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
                  <p class="text-2xl font-semibold text-gray-900">{{ tasks.length }}</p>
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
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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
  
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <TaskCard 
              v-for="task in tasks" 
              :key="task.id" 
              :task="task" 
              @view="viewTaskDetails"
            />
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import TaskboardNavigation from '@/components/TaskboardNavigation.vue'
  import TaskCard from '@/components/TaskCard.vue'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const fetchDepartmentTasks = async () => {
    loading.value = true
    error.value = null
    
    try {
      const userId = authStore.user.id
      
      // Get user's team and department info
      const userResponse = await fetch(`http://localhost:8000/user/${userId}`)
      if (!userResponse.ok) throw new Error('Failed to fetch user data')
      const userData = await userResponse.json()
      
      const teamId = userData.team_id
      
      if (!teamId) {
        tasks.value = []
        error.value = 'You are not assigned to a team or department'
        return
      }
      
      // Get team info to find department_id
      const teamsResponse = await fetch(`http://localhost:8000/teams`)
      if (!teamsResponse.ok) throw new Error('Failed to fetch teams')
      const allTeams = await teamsResponse.json()
      
      const userTeam = allTeams.find(team => team.id === teamId)
      
      if (!userTeam || !userTeam.department_id) {
        tasks.value = []
        error.value = 'Team is not assigned to a department'
        return
      }
      
      const departmentId = userTeam.department_id
      
      // Get all teams in the same department
      const departmentTeams = allTeams.filter(team => team.department_id === departmentId)
      const departmentTeamIds = departmentTeams.map(team => team.id)
      
      // Get all users in those teams
      const usersResponse = await fetch(`http://localhost:8000/users`)
      if (!usersResponse.ok) throw new Error('Failed to fetch users')
      const allUsers = await usersResponse.json()
      
      const departmentUsers = allUsers.filter(user => 
        user.team_id && departmentTeamIds.includes(user.team_id)
      )
      const departmentUserIds = departmentUsers.map(user => user.id)
      
      // Fetch tasks for all department users
      const taskPromises = departmentUserIds.map(memberId => 
      fetch(`http://localhost:8000/tasks?owner_id=${memberId}`)
          .then(res => res.ok ? res.json() : [])
      )
      
      const departmentTasksArrays = await Promise.all(taskPromises)
      tasks.value = departmentTasksArrays.flat()
      
    } catch (err) {
      console.error('Error fetching department tasks:', err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  const getTaskCountByStatus = (status) => {
    return tasks.value.filter(task => task.status === status).length
  }
  
  const viewTaskDetails = (taskId) => {
    router.push(`/tasks/${taskId}`)
  }
  
  onMounted(() => {
    fetchDepartmentTasks()
  })
  </script>