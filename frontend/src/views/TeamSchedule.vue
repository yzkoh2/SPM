<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Team Schedule</h1>
        <p class="text-gray-600 mt-2">View all team tasks in calendar format</p>
      </div>

      <TaskCalendar :tasks="filteredTasks" :is-personal="false" :loading="loading" subtitle="Team tasks scheduled this month"
        @view-task="viewTaskDetails">
        <template #filters>
          <select v-model="filters.memberName"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">All Members</option>
            <option v-for="member in teamMembers" :key="member.id" :value="member.name">
              {{ member.name }}
            </option>
          </select>

          <select v-model="filters.status"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
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
const KONG_API_URL = "http://localhost:8000"

const tasks = ref([])
const loading = ref(true)
const teamMembers = ref([])

const filters = ref({
  memberName: '',
  status: ''
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.memberName) {
    // Find the member ID from the selected member name
    const selectedMember = teamMembers.value.find(m => m.name === filters.value.memberName)
    
    if (selectedMember) {
      filtered = filtered.filter(task => {
        // Check if the member is the owner
        const isOwner = task.owner_id === selectedMember.id
        
        // Check if the member is a collaborator
        const isCollaborator = task.collaborator_ids && 
                               task.collaborator_ids.includes(selectedMember.id)
        
        return isOwner || isCollaborator
      })
    }
  }

  if (filters.value.status) {
    filtered = filtered.filter(task => task.status === filters.value.status)
  }

  return filtered
})

const getTeamMemberIds = async (teamId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/user/team/${teamId}`)
    const members = await response.json()
    teamMembers.value = members
    return members.map(member => member.id)
  } catch (err) {
    console.error('Error fetching team members:', err)
    return []
  }
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

  try {
    const userId = authStore.user.id

    const userResponse = await fetch(`${KONG_API_URL}/user/${userId}`)
    const userData = await userResponse.json()
    const teamId = userData.team_id
    const memberIds = await getTeamMemberIds(teamId)
    
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
    // Fetch user details for all unique owner IDs
    const uniqueOwnerIds = [...new Set(relevantTasks.map(task => task.owner_id).filter(id => id))]
    const userCache = {}
    
    await Promise.all(
      uniqueOwnerIds.map(async (ownerId) => {
        const userDetails = await fetchUserDetails(ownerId)
        if (userDetails) {
          userCache[ownerId] = userDetails.name || `User ${ownerId}`
        }
      })
    )

    // Append owner names to tasks
    const relevantTasksWithOwners = relevantTasks.map(task => ({
      ...task,
      owner_name: task.owner_id ? userCache[task.owner_id] || 'Unknown' : 'Unassigned'
    }))

    tasks.value = relevantTasksWithOwners

  } catch (err) {
    console.error('Error fetching team tasks:', err)
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