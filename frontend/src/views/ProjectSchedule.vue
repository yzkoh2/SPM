<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Project Schedule</h1>
        <p class="text-gray-600 mt-2">
          View all tasks of your project team members (including standalone tasks)
        </p>
      </div>

      <TaskCalendar
        :tasks="filteredTasks"
        :is-personal="false"
        :loading="loading"
        subtitle="All tasks from project collaborators scheduled this month"
        @view-task="viewTaskDetails"
      >
        <template #filters>
          <select
            v-model="filters.projectId"
            @change="fetchTasks"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Project Members</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.title }} Team
            </option>
          </select>

          <select
            v-model="filters.memberName"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Members</option>
            <option v-for="member in projectMembers" :key="member.id" :value="member.name">
              {{ member.name }}
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
const projects = ref([])
const projectMembers = ref([])
const loading = ref(true)

const filters = ref({
  projectId: '',
  memberName: '',
  status: '',
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.projectId) {
    // Filter to show only tasks from members of the selected project
    const projectId = parseInt(filters.value.projectId)
    const project = projects.value.find((p) => p.id === projectId)

    if (project && project.member_ids) {
      filtered = filtered.filter((task) => {
        const isOwner = project.member_ids.includes(task.owner_id)
        const isCollaborator =
          task.collaborator_ids &&
          task.collaborator_ids.some((id) => project.member_ids.includes(id))
        return isOwner || isCollaborator
      })
    }
  }

  if (filters.value.memberName) {
    // Find the member ID from the selected member name
    const selectedMember = projectMembers.value.find((m) => m.name === filters.value.memberName)

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

const fetchProjects = async () => {
  try {
    const userId = authStore.currentUserId
    const response = await fetch(`${KONG_API_URL}/projects/user/${userId}`)
    const data = await response.json()

    // Fetch collaborators for each project to get member IDs
    for (const project of data) {
      const collaboratorsResponse = await fetch(
        `${KONG_API_URL}/projects/${project.id}/collaborators`,
      )
      if (collaboratorsResponse.ok) {
        const collaborators = await collaboratorsResponse.json()
        // Include project owner and all collaborators as member IDs
        project.member_ids = [
          project.owner_id,
          ...collaborators.map((c) => c.user_id),
        ]
      } else {
        project.member_ids = [project.owner_id]
      }
    }

    projects.value = data
    console.log('Fetched projects with members:', data)
  } catch (error) {
    console.error('Error fetching projects:', error)
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

const getAllProjectMemberIds = () => {
  // Get unique member IDs from all projects
  const memberIdSet = new Set()

  projects.value.forEach((project) => {
    if (project.member_ids) {
      project.member_ids.forEach((id) => memberIdSet.add(id))
    }
  })

  return Array.from(memberIdSet)
}

const fetchTasks = async () => {
  try {
    loading.value = true
    await fetchProjects()

    // Get all unique member IDs from all projects
    const memberIds = getAllProjectMemberIds()

    if (memberIds.length === 0) {
      tasks.value = []
      projectMembers.value = []
      return
    }

    console.log('Fetching ALL tasks for project members:', memberIds)

    // Fetch ALL tasks owned by any project member (not just project tasks)
    const taskPromises = memberIds.map((memberId) =>
      fetch(`${KONG_API_URL}/tasks?owner_id=${memberId}`)
        .then((res) => (res.ok ? res.json() : []))
        .catch(() => []),
    )

    const ownedTasksArrays = await Promise.all(taskPromises)
    const ownedTasks = ownedTasksArrays.flat()

    console.log('Fetched owned tasks:', ownedTasks.length)

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

        // Check if any collaborator is a project member
        const hasProjectCollaborator = collaboratorIds.some((collabId) =>
          memberIds.includes(collabId),
        )

        if (hasProjectCollaborator) {
          taskMap.get(taskId).has_project_collaborator = true
        }
      }
    })

    // Filter to only include tasks owned by or collaborated on by project members
    const relevantTasks = Array.from(taskMap.values()).filter((task) => {
      return memberIds.includes(task.owner_id) || task.has_project_collaborator
    })

    console.log('Relevant tasks after filtering:', relevantTasks.length)

    // Fetch user details for all unique owner IDs
    const uniqueOwnerIds = [
      ...new Set(relevantTasks.map((task) => task.owner_id).filter((id) => id)),
    ]
    const userCache = {}

    await Promise.all(
      uniqueOwnerIds.map(async (ownerId) => {
        const userDetails = await fetchUserDetails(ownerId)
        if (userDetails) {
          userCache[ownerId] = userDetails
        }
      }),
    )

    // Store project members for filtering
    projectMembers.value = Object.values(userCache)

    // Append owner names to tasks
    const tasksWithOwners = relevantTasks.map((task) => ({
      ...task,
      owner_name: task.owner_id ? userCache[task.owner_id]?.name || 'Unknown' : 'Unassigned',
    }))

    tasks.value = tasksWithOwners
    console.log('Final tasks with owners:', tasks.value.length)
  } catch (error) {
    console.error('Error fetching tasks:', error)
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