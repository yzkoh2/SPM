import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useTaskboard() {
  const authStore = useAuthStore()
  const tasks = ref([])
  const teamMembers = ref([])
  const departmentMembers = ref([])
  const memberIds = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Filter states
  const filters = ref({
    member: '',
    status: '',
    deadline: '',
  })

  const sortBy = ref('default')

  /**
   * Fetch collaborators for a specific task
   */
  const fetchCollaboratorsForTask = async (taskId) => {
    try {
      const response = await fetch(`http://localhost:8000/tasks/${taskId}/collaborators`)
      if (response.ok) {
        const collaborators = await response.json()
        return collaborators.map((c) => c.user_id)
      }
      return []
    } catch (err) {
      console.error(`Error fetching collaborators for task ${taskId}:`, err)
      return []
    }
  }

  /**
   * Main fetch function that retrieves tasks where team/department members
   * are either owners OR collaborators
   */
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
        error.value =
          scope === 'team'
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

      memberIds.value = userIds

      if (userIds.length === 0) {
        tasks.value = []
        return
      }

      // Step 1: Fetch tasks owned by members
      const taskPromises = userIds.map((memberId) =>
        fetch(`http://localhost:8000/tasks?owner_id=${memberId}`)
          .then((res) => (res.ok ? res.json() : []))
          .catch(() => []),
      )

      const ownedTasksArrays = await Promise.all(taskPromises)
      const ownedTasks = ownedTasksArrays.flat()

      // Step 2: Create a map to track unique tasks
      const taskMap = new Map()
      ownedTasks.forEach((task) => {
        taskMap.set(task.id, { ...task, collaborator_ids: [] })
      })

      // Step 3: Fetch collaborators for each task
      const collaboratorPromises = Array.from(taskMap.keys()).map(async (taskId) => {
        const collaboratorIds = await fetchCollaboratorsForTask(taskId)
        return { taskId, collaboratorIds }
      })

      const collaboratorResults = await Promise.all(collaboratorPromises)

      // Step 4: Add collaborator IDs to tasks and check if any member is a collaborator
      collaboratorResults.forEach(({ taskId, collaboratorIds }) => {
        if (taskMap.has(taskId)) {
          taskMap.get(taskId).collaborator_ids = collaboratorIds

          // Check if any member is a collaborator on this task
          const hasMemberCollaborator = collaboratorIds.some((collabId) =>
            userIds.includes(collabId),
          )

          if (hasMemberCollaborator) {
            taskMap.get(taskId).has_member_collaborator = true
          }
        }
      })

      // Step 5: Filter to only include tasks where members are owner OR collaborator
      const relevantTasks = Array.from(taskMap.values()).filter((task) => {
        return userIds.includes(task.owner_id) || task.has_member_collaborator
      })

      tasks.value = relevantTasks
    } catch (err) {
      console.error(`Error fetching ${scope} tasks:`, err)
      error.value = err.message
      tasks.value = []
    } finally {
      loading.value = false
    }
  }

  const getTeamMemberIds = async (teamId) => {
    const response = await fetch(`http://localhost:8000/user/team/${teamId}`)
    if (!response.ok) throw new Error('Failed to fetch team members')

    const members = await response.json()
    teamMembers.value = members
    return members.map((member) => member.id)
  }

  const getDepartmentMemberIds = async (teamId) => {
    // Get all teams to find which department this team belongs to
    const teamsResponse = await fetch(`http://localhost:8000/user/teams`)
    if (!teamsResponse.ok) throw new Error('Failed to fetch teams')

    const allTeams = await teamsResponse.json()
    const userTeam = allTeams.find((team) => team.id === teamId)

    if (!userTeam || !userTeam.department_id) {
      throw new Error('Team is not assigned to a department')
    }

    const departmentId = userTeam.department_id

    const usersResponse = await fetch(`http://localhost:8000/user/department/${departmentId}`)
    if (!usersResponse.ok) throw new Error('Failed to fetch department users')

    const members = await usersResponse.json()
    departmentMembers.value = members
    return members.map((user) => user.id)
  }

  // Computed property for filtered and sorted tasks
  const filteredAndSortedTasks = computed(() => {
    let filtered = [...tasks.value]

    // Filter by member (checks both owner and collaborators)
    if (filters.value.member) {
      const memberId = parseInt(filters.value.member)
      filtered = filtered.filter((task) => {
        // Check if member is owner
        if (task.owner_id === memberId) return true

        // Check if member is collaborator
        if (task.collaborator_ids && task.collaborator_ids.includes(memberId)) return true

        return false
      })
    }

    // Filter by status
    if (filters.value.status) {
      filtered = filtered.filter((task) => task.status === filters.value.status)
    }

    // Filter by deadline
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

    // Sort by deadline
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

    return filtered
  })

  const getTaskCountByStatus = (status) => {
    return filteredAndSortedTasks.value.filter((task) => task.status === status).length
  }

  const getTasksByOwner = (ownerId) => {
    return filteredAndSortedTasks.value.filter((task) => task.owner_id === ownerId)
  }

  const getTasksByStatus = (status) => {
    return filteredAndSortedTasks.value.filter((task) => task.status === status)
  }

  const clearFilters = () => {
    filters.value.member = ''
    filters.value.status = ''
    filters.value.deadline = ''
    sortBy.value = 'default'
  }

  const applyFilters = () => {
    // Filters are applied automatically via computed property
    // This method is kept for compatibility
  }

  return {
    tasks,
    teamMembers,
    departmentMembers,
    memberIds,
    loading,
    error,
    filters,
    sortBy,
    fetchTasks,
    filteredAndSortedTasks,
    getTaskCountByStatus,
    getTasksByOwner,
    getTasksByStatus,
    clearFilters,
    applyFilters,
  }
}
