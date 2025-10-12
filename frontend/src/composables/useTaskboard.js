import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useTaskboard() {
  const authStore = useAuthStore()
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchTasks = async (scope = 'team') => {
    loading.value = true
    error.value = null
    
    try {
      const userId = authStore.user.id
      
      // Fetch user data
      const userResponse = await fetch(`http://localhost:8000/user/${userId}`)
      if (!userResponse.ok) throw new Error('Failed to fetch user data')
      const userData = await userResponse.json()
      
      const teamId = userData.team_id
      if (!teamId) {
        tasks.value = []
        error.value = scope === 'team' 
          ? 'You are not assigned to a team' 
          : 'You are not assigned to a team or department'
        return
      }

      let userIds = []

      if (scope === 'team') {
        userIds = await getTeamMemberIds(teamId)
      } else if (scope === 'department') {
        userIds = await getDepartmentMemberIds(teamId)
      }

      if (userIds.length === 0) {
        tasks.value = []
        return
      }

      // Fetch tasks for all members (one call per member)
      const taskPromises = userIds.map(memberId => 
        fetch(`http://localhost:8000/tasks?owner_id=${memberId}`)
          .then(res => res.ok ? res.json() : [])
          .catch(() => []) // Handle individual failures gracefully
      )
      
      const teamTasksArrays = await Promise.all(taskPromises)
      tasks.value = teamTasksArrays.flat()
      
    } catch (err) {
      console.error(`Error fetching ${scope} tasks:`, err)
      error.value = err.message
      tasks.value = []
    } finally {
      loading.value = false
    }
  }

  const getTeamMemberIds = async (teamId) => {
    // Use your Flask endpoint: /user/team/{team_id}
    const response = await fetch(`http://localhost:8000/user/team/${teamId}`)
    if (!response.ok) throw new Error('Failed to fetch team members')
    
    const teamMembers = await response.json()
    return teamMembers.map(member => member.id)
  }

  const getDepartmentMemberIds = async (teamId) => {
    // Get all teams to find which department this team belongs to
    const teamsResponse = await fetch(`http://localhost:8000/user/teams`)
    if (!teamsResponse.ok) throw new Error('Failed to fetch teams')
    
    const allTeams = await teamsResponse.json()
    const userTeam = allTeams.find(team => team.id === teamId)
    
    if (!userTeam || !userTeam.department_id) {
      throw new Error('Team is not assigned to a department')
    }

    const departmentId = userTeam.department_id

    // Use your Flask endpoint: /user/department/{dept_id}
    const usersResponse = await fetch(
      `http://localhost:8000/user/department/${departmentId}`
    )
    if (!usersResponse.ok) throw new Error('Failed to fetch department users')
    
    const departmentUsers = await usersResponse.json()
    return departmentUsers.map(user => user.id)
  }

  const getTaskCountByStatus = (status) => {
    return tasks.value.filter(task => task.status === status).length
  }

  const getTasksByOwner = (ownerId) => {
    return tasks.value.filter(task => task.owner_id === ownerId)
  }

  const getTasksByStatus = (status) => {
    return tasks.value.filter(task => task.status === status)
  }

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    getTaskCountByStatus,
    getTasksByOwner,
    getTasksByStatus
  }
}