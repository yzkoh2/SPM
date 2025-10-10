<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Project Schedule</h1>
        <p class="text-gray-600 mt-2">View all project tasks in calendar format</p>
      </div>

      <TaskCalendar :tasks="filteredTasks" :loading="loading" subtitle="Project tasks scheduled this month"
        @view-task="viewTaskDetails">
        <template #filters>
          <select v-model="filters.projectId" @change="fetchTasks"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">All Projects</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.title }}
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
const projects = ref([])
const loading = ref(true)

const filters = ref({
  projectId: '',
  status: ''
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.projectId) {
    filtered = filtered.filter(task => task.project_id === parseInt(filters.value.projectId))
  }

  if (filters.value.status) {
    filtered = filtered.filter(task => task.status === filters.value.status)
  }

  return filtered
})

const fetchProjects = async () => {
  try {
    const userId = authStore.currentUserId
    const response = await fetch(`${KONG_API_URL}/projects/user/${userId}`)
    const data = await response.json()
    projects.value = data
    console.log('Fetched projects:', data)
  } catch (error) {
    console.error('Error fetching projects:', error)
  }
}

const fetchTasks = async () => {
  try {
    loading.value = true
    const userId = authStore.currentUserId
    await fetchProjects()

    // Get project IDs
    const projectIds = projects.value.map(p => p.id)

    if (projectIds.length === 0) {
      tasks.value = []
      return
    }

    // Fetch tasks for all projects
    const allTasks = []
    for (const projectId of projectIds) {
      const response = await fetch(`${KONG_API_URL}/projects/${projectId}/tasks`)
      if (!response.ok) {
        console.error(`Failed to fetch tasks for project ${projectId}`)
        continue
      }
      const projectTasks = await response.json()
      allTasks.push(...projectTasks)
    }
    tasks.value = allTasks
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