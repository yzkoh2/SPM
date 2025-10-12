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
          <button 
            @click="fetchTasks('team')" 
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
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z">
          </path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No team tasks found</h3>
        <p class="mt-1 text-sm text-gray-500">Your team members haven't created any tasks yet.</p>
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
  fetchTasks('team')
})
</script>