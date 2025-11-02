<template>
  <div
    class="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border-l-4 cursor-pointer transform hover:-translate-y-1"
    :class="statusBorderColor"
    @click="emit('view', task.id)"
  >
    <div class="p-5">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <!-- Priority Badge -->
          <div class="flex items-center space-x-2 mb-2">
            <div
              class="flex items-center px-2.5 py-1 rounded-md font-bold text-sm"
              :class="getPriorityColorClass(task.priority)"
            >
              <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd"
                />
              </svg>
              Priority: {{ task.priority || 'N/A' }}
            </div>
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="statusBadgeColor"
            >
              {{ task.status }}
            </span>
          </div>

          <h3
            class="text-lg font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors"
          >
            {{ task.title }}
          </h3>
          <RecurringIcon
            :isRecurring="task.is_recurring"
            :recurrenceInterval="task.recurrence_interval"
            :recurrenceDays="task.recurrence_days"
          />
        </div>

        <div class="flex items-center space-x-1 ml-4">
          <button
            v-if="authStore.user && task.owner_id == authStore.user.id"
            @click.stop="task.status !== 'Completed' && emit('edit', task)"
            :disabled="task.status === 'Completed'"
            :class="[
              'p-1 rounded-full transition-colors',
              task.status === 'Completed'
                ? 'text-gray-300 cursor-not-allowed'
                : 'text-gray-400 hover:text-indigo-600 hover:bg-gray-100 cursor-pointer'
            ]"
            :title="task.status === 'Completed' ? 'Cannot edit completed task' : 'Edit Task'"
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
            v-if="authStore.user && task.owner_id == authStore.user.id"
            @click.stop="emit('delete', task.id)"
            class="text-gray-400 hover:text-red-600 transition-colors p-1 rounded-full hover:bg-red-50"
            title="Delete Task"
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
        {{ task.description || 'No description available.' }}
      </p>

      <div v-if="task.deadline" class="flex items-center mt-4 text-sm">
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
        <span :class="deadlineColor"> Due: {{ formatDeadline(task.deadline) }} </span>
      </div>

      <div class="mt-4 pt-4 border-t border-gray-100">
        <div class="flex justify-between items-center text-xs text-gray-500">
          <div class="flex items-center space-x-3">
            <span class="flex items-center" title="Subtasks">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                ></path>
              </svg>
              {{ task.subtask_count || 0 }}
            </span>
            <span class="flex items-center" title="Comments">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                ></path>
              </svg>
              {{ task.comment_count || 0 }}
            </span>
            <span class="flex items-center" title="Attachments">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                ></path>
              </svg>
              {{ task.attachment_count || 0 }}
            </span>
          </div>
          <span class="font-medium">Owner ID: {{ task.owner_id }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import RecurringIcon from '@/components/RecurringIcon.vue'

const authStore = useAuthStore()

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['view', 'edit', 'delete'])

const statusBorderColor = computed(() => {
  const colors = {
    Unassigned: 'border-gray-400',
    Ongoing: 'border-yellow-400',
    'Under Review': 'border-orange-400',
    Completed: 'border-green-400',
  }
  return colors[props.task.status] || 'border-gray-400'
})

const statusBadgeColor = computed(() => {
  const colors = {
    Unassigned: 'bg-gray-100 text-gray-800',
    Ongoing: 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    Completed: 'bg-green-100 text-green-800',
  }
  return colors[props.task.status] || 'bg-gray-100 text-gray-800'
})

const deadlineColor = computed(() => {
  if (!props.task.deadline) return 'text-gray-600'
  const now = new Date()
  const deadlineDate = new Date(props.task.deadline)
  if (deadlineDate < now) return 'text-red-600 font-medium'
  // Reset time part for today's comparison
  now.setHours(0, 0, 0, 0)
  deadlineDate.setHours(0, 0, 0, 0)
  if (deadlineDate.getTime() === now.getTime()) return 'text-orange-600 font-medium'
  return 'text-gray-900'
})

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline set'
  const date = new Date(deadline)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Priority color classes based on priority level
const getPriorityColorClass = (priority) => {
  if (!priority) return 'bg-gray-100 text-gray-700 border border-gray-300'

  if (priority >= 8 && priority <= 10) {
    return 'bg-red-100 text-red-800 border border-red-300' // High
  } else if (priority >= 4 && priority <= 7) {
    return 'bg-yellow-100 text-yellow-800 border border-yellow-300' // Medium
  } else if (priority >= 1 && priority <= 3) {
    return 'bg-green-100 text-green-800 border border-green-300' // Low
  }
  return 'bg-gray-100 text-gray-700 border border-gray-300'
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
