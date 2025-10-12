<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Department Taskboard</h1>
        <p class="text-sm text-gray-600 mt-1">View and manage tasks across all teams in your department</p>
      </div>

      <TaskboardNavigation />

      <!-- Error State -->
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
          <button 
            @click="fetchTasks('department')" 
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors"
          >
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
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4">
          </path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No department tasks found</h3>
        <p class="mt-1 text-sm text-gray-500">Your department members haven't created any tasks yet.</p>
      </div>

      <!-- Task Dashboard -->
      <div v-else>
        <!-- Status Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <TaskStatusCard
            title="Total Tasks"
            :count="tasks.length"
            icon="clipboard"
            color="blue"
          />
          <TaskStatusCard
            title="Unassigned"
            :count="getTaskCountByStatus('Unassigned')"
            icon="clock"
            color="gray"
          />
          <TaskStatusCard
            title="In Progress"
            :count="getTaskCountByStatus('In Progress')"
            icon="spinner"
            color="yellow"
          />
          <TaskStatusCard
            title="Completed"
            :count="getTaskCountByStatus('Completed')"
            icon="check"
            color="green"
          />
        </div>

        <!-- Task Cards Grid -->
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TaskboardNavigation from '@/components/TaskboardNavigation.vue'
import TaskCard from '@/components/TaskCard.vue'
import TaskStatusCard from '@/components/TaskStatusCard.vue'
import { useTaskboard } from '@/composables/useTaskboard'

const router = useRouter()
const { tasks, loading, error, fetchTasks, getTaskCountByStatus } = useTaskboard()

const viewTaskDetails = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

onMounted(() => {
  fetchTasks('department')
})
</script>