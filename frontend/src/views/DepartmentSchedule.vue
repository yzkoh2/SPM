<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Department Schedule</h1>
        <p class="text-gray-600 mt-2">View all department tasks in calendar format</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
        <div class="flex items-center mb-4">
          <svg
            class="w-6 h-6 text-red-600 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <h3 class="text-lg font-medium text-red-800">Error Loading Department Tasks</h3>
        </div>
        <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
        <div class="mt-4">
          <button
            @click="fetchTasks"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>

      <TaskCalendar
        :tasks="filteredTasks"
        :is-personal="false"
        :loading="loading"
        subtitle="Department tasks scheduled this month"
        @view-task="viewTaskDetails"
      >
        <template #filters>
          <select
            v-model="filters.memberName"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Department Members</option>
            <option v-for="member in departmentMembers" :key="member.id" :value="member.name">
              {{ member.name }} ({{ member.team || 'No Team' }})
            </option>
          </select>

          <select
            v-model="filters.status"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="Unassigned">Unassigned</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Under Review">Under Review</option>
            <option value="Completed">Completed</option>
          </select>
        </template>
      </TaskCalendar>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TaskCalendar from '@/components/TaskCalendar.vue'

const router = useRouter()
const authStore = useAuthStore()
const KONG_API_URL = 'http://localhost:8000'

const tasks = ref([])
const loading = ref(true)
const departmentMembers = ref([])
const error = ref(null)

const filters = ref({
  memberName: '',
  status: '',
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.memberName) {
    // Find the member ID from the selected member name
    const selectedMember = departmentMembers.value.find((m) => m.name === filters.value.memberName)

    if (selectedMember) {
      filtered = filtered.filter((task) => {
        // Check if the member is the owner
        const isOwner = task.owner_id === selectedMember.id

        // Check if the member is a collaborator
        const isCollaborator =
          task.collaborator_ids && task.collaborator_ids.includes(selectedMember.id)

        return isOwner || isCollaborator
      })
    }
  }

  if (filters.value.status) {
    filtered = filtered.filter((task) => task.status === filters.value.status)
  }

  return filtered
})

const getDepartmentMemberIds = async (teamId) => {
  // First, get all teams to find the user's department
  const teamsResponse = await fetch(`${KONG_API_URL}/user/teams`)
  if (!teamsResponse.ok) throw new Error('Failed to fetch teams')

  const allTeams = await teamsResponse.json()
  const userTeam = allTeams.find((team) => team.id === teamId)

  if (!userTeam || !userTeam.department_id) {
    throw new Error('Team is not assigned to a department')
  }

  const departmentId = userTeam.department_id

  // Fetch all users in the department
  const usersResponse = await fetch(`${KONG_API_URL}/user/department/${departmentId}`)
  if (!usersResponse.ok) throw new Error('Failed to fetch department users')

  const members = await usersResponse.json()
  departmentMembers.value = members
  return members.map((user) => user.id)
}

const fetchCollaboratorsForTask = async (taskId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/collaborators`)
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

const fetchUserDetails = async (userId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/user/${userId}`)

    if (response.ok) {
      return await response.json()
    } else {
      console.warn(`Failed to load user details for ID ${userId}`)
      return null
    }
  } catch (err) {
    console.error(`Error fetching user ${userId}:`, err)
    return null
  }
}

const fetchTasks = async () => {
  loading.value = true
  error.value = null

  try {
    const userId = authStore.user.id

    // Get user data to find their team
    const userResponse = await fetch(`${KONG_API_URL}/user/${userId}`)
    if (!userResponse.ok) throw new Error('Failed to fetch user data')
    const userData = await userResponse.json()

    const teamId = userData.team_id
    if (!teamId) {
      tasks.value = []
      error.value = 'You are not assigned to a team or department'
      return
    }

    // Get all department member IDs
    const memberIds = await getDepartmentMemberIds(teamId)

    if (memberIds.length === 0) {
      tasks.value = []
      return
    }

    // Fetch tasks owned by all department members
    const taskPromises = memberIds.map((memberId) =>
      fetch(`${KONG_API_URL}/tasks?owner_id=${memberId}`)
        .then((res) => (res.ok ? res.json() : []))
        .catch(() => []),
    )

    const ownedTasksArrays = await Promise.all(taskPromises)
    const ownedTasks = ownedTasksArrays.flat()

    // Create a map to store unique tasks with collaborator info
    const taskMap = new Map()
    ownedTasks.forEach((task) => {
      taskMap.set(task.id, { ...task, collaborator_ids: [] })
    })

    // Fetch collaborators for all tasks
    const collaboratorPromises = Array.from(taskMap.keys()).map(async (taskId) => {
      const collaboratorIds = await fetchCollaboratorsForTask(taskId)
      return { taskId, collaboratorIds }
    })

    const collaboratorResults = await Promise.all(collaboratorPromises)

    // Add collaborator info to tasks
    collaboratorResults.forEach(({ taskId, collaboratorIds }) => {
      if (taskMap.has(taskId)) {
        taskMap.get(taskId).collaborator_ids = collaboratorIds

        // Check if any collaborator is from the department
        const hasDepartmentCollaborator = collaboratorIds.some((collabId) =>
          memberIds.includes(collabId),
        )

        if (hasDepartmentCollaborator) {
          taskMap.get(taskId).has_department_collaborator = true
        }
      }
    })

    // Filter to only include tasks owned by or collaborated on by department members
    const relevantTasks = Array.from(taskMap.values()).filter((task) => {
      return memberIds.includes(task.owner_id) || task.has_department_collaborator
    })
    // Fetch user details for all unique owner IDs
    const uniqueOwnerIds = [
      ...new Set(relevantTasks.map((task) => task.owner_id).filter((id) => id)),
    ]
    const userCache = {}

    await Promise.all(
      uniqueOwnerIds.map(async (ownerId) => {
        const userDetails = await fetchUserDetails(ownerId)
        if (userDetails) {
          userCache[ownerId] = userDetails.name || `User ${ownerId}`
        }
      }),
    )

    // Append owner names to tasks
    const relevantTasksWithOwners = relevantTasks.map((task) => ({
      ...task,
      owner_name: task.owner_id ? userCache[task.owner_id] || 'Unknown' : 'Unassigned',
    }))

    tasks.value = relevantTasksWithOwners
  } catch (err) {
    console.error('Error fetching department tasks:', err)
    error.value = err.message
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

onMounted(() => {
  fetchTasks()
})
</script>
