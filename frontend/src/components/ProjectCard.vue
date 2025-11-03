<template>
  <div
    class="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border-l-4 cursor-pointer transform hover:-translate-y-1"
    :class="roleBorderColor"
    @click="emit('view', project.id)"
  >
    <div class="p-5">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <!-- Role Badge -->
          <div class="flex items-center space-x-2 mb-2">
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="roleBadgeColor"
            >
              {{ project.user_role === 'owner' ? 'Owner' : 'Collaborator' }}
            </span>
          </div>

          <h3 class="text-lg font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors">
            {{ project.title }}
          </h3>
        </div>

        <div class="flex items-center space-x-1 ml-4">
          <button
            v-if="authStore.user && project.user_role === 'owner'"
            @click.stop="emit('edit', project)"
            class="text-gray-400 hover:text-indigo-600 transition-colors p-1 rounded-full hover:bg-gray-100 cursor-pointer"
            title="Edit Project"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              ></path>
            </svg>
          </button>
          <button
            v-if="authStore.user && project.user_role === 'owner'"
            @click.stop="emit('delete', project.id)"
            class="text-gray-400 hover:text-red-600 transition-colors p-1 rounded-full hover:bg-red-50"
            title="Delete Project"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              ></path>
            </svg>
          </button>
        </div>
      </div>

      <p class="text-sm text-gray-600 mt-3 h-10 line-clamp-2">
        {{ project.description || 'No description available.' }}
      </p>

      <div v-if="project.deadline" class="flex items-center mt-4 text-sm">
        <svg
          class="w-4 h-4 text-gray-400 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          ></path>
        </svg>
        <span :class="deadlineColor">{{ formatDeadline }}</span>
      </div>

      <!-- Project Stats -->
      <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
        <div class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            ></path>
          </svg>
          {{ project.task_count || 0 }} tasks
        </div>
        <div class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            ></path>
          </svg>
          {{ project.collaborator_ids?.length || 0 }} members
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const props = defineProps({
  project: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['view', 'edit', 'delete'])

// Border color based on role
const roleBorderColor = computed(() => {
  return props.project.user_role === 'owner'
    ? 'border-l-indigo-500'
    : 'border-l-blue-400'
})

// Badge color based on role
const roleBadgeColor = computed(() => {
  return props.project.user_role === 'owner'
    ? 'bg-indigo-100 text-indigo-800'
    : 'bg-blue-100 text-blue-800'
})

// Deadline formatting
const formatDeadline = computed(() => {
  if (!props.project.deadline) return 'No deadline'
  const deadline = new Date(props.project.deadline)
  return deadline.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
})

// Deadline color
const deadlineColor = computed(() => {
  if (!props.project.deadline) return 'text-gray-500'

  const now = new Date()
  const deadline = new Date(props.project.deadline)
  const daysUntilDeadline = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24))

  if (daysUntilDeadline < 0) return 'text-red-600 font-medium'
  if (daysUntilDeadline <= 3) return 'text-orange-600 font-medium'
  if (daysUntilDeadline <= 7) return 'text-yellow-600 font-medium'
  return 'text-gray-600'
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
