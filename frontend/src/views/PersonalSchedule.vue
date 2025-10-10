<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Personal Schedule</h1>
        <p class="text-gray-600 mt-2">View all your personal and collaborated tasks</p>
      </div>

      <TaskCalendar
        :tasks="filteredTasks"
        :loading="loading"
        subtitle="Your personal tasks this month"
        @view-task="viewTaskDetails"
      >
        <template #filters>
          <select v-model="filters.type"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">All</option>
            <option value="owned">Owned</option>
            <option value="collab">Collaborated</option>
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

const filters = ref({
  type: '', // 'owned' or 'collab'
  status: ''
})

const fetchTasks = async () => {
  try {
    loading.value = true
    const userId = authStore.currentUserId

    const response = await fetch(`${KONG_API_URL}/tasks?owner_id=${userId}`)
    if (!response.ok) throw new Error(`Failed to fetch tasks: ${response.statusText}`)

    const data = await response.json()

    // Mark ownership for filtering
    tasks.value = data.map(task => ({
      ...task,
      is_owner: task.owner_id === userId
    }))
  } catch (error) {
    console.error('Error fetching tasks:', error)
  } finally {
    loading.value = false
  }
}

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (filters.value.type === 'owned') {
    filtered = filtered.filter(t => t.is_owner)
  } else if (filters.value.type === 'collab') {
    filtered = filtered.filter(t => !t.is_owner)
  }

  if (filters.value.status) {
    filtered = filtered.filter(t => t.status === filters.value.status)
  }

  return filtered
})

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

onMounted(fetchTasks)
</script>

