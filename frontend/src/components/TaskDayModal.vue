<template>
  <div
    @click="$emit('close')"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
  >
    <div
      @click.stop
      class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
    >
      <div
        class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-4 flex justify-between items-center"
      >
        <div>
          <h3 class="text-xl font-bold text-white">{{ formatModalDate(day?.date) }}</h3>
          <p class="text-indigo-100 text-sm mt-1">
            {{ day?.tasks.length }} {{ day?.tasks.length === 1 ? 'task' : 'tasks' }}
          </p>
        </div>
        <button
          @click="$emit('close')"
          class="text-white hover:bg-indigo-500 rounded-lg p-2 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <div class="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
        <div class="space-y-4">
          <div
            v-for="task in day?.tasks"
            :key="task.id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
            @click="$emit('view-task', task.id)"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900 text-lg">{{ task.title }}</h4>
                <div class="flex items-center gap-2 mt-2">
                  <span
                    :class="[
                      'px-3 py-1 rounded-full text-xs font-medium',
                      getStatusBadgeColor(task.status),
                    ]"
                  >
                    {{ task.status }}
                  </span>
                  <span
                    v-if="showOwnerBadge && task.is_owner !== undefined"
                    :class="[
                      'px-3 py-1 rounded-full text-xs font-medium',
                      task.is_owner
                        ? 'bg-indigo-100 text-indigo-800'
                        : 'bg-green-100 text-green-800',
                    ]"
                  >
                    {{ task.is_owner ? 'Owner' : 'Collaborator' }}
                  </span>
                </div>
              </div>
              <svg
                class="w-5 h-5 text-gray-400 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                ></path>
              </svg>
            </div>

            <div class="space-y-2 text-sm text-gray-600">
              <div v-if="task.description" class="flex items-start">
                <svg
                  class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M4 6h16M4 12h16M4 18h7"
                  ></path>
                </svg>
                <p class="line-clamp-2">{{ task.description }}</p>
              </div>

              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                <span :class="getDeadlineTextColor(task.deadline)">
                  {{ formatFullDateTime(task.deadline) }}
                </span>
              </div>

              <div v-if="task.project_id" class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  ></path>
                </svg>
                <span>Project ID: {{ task.project_id }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-gray-50 px-6 py-4 flex justify-end">
        <button
          @click="$emit('close')"
          class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCalendarUtils } from '@/composables/calendarUtils'

defineProps({
  day: { type: Object, required: true },
  showOwnerBadge: { type: Boolean, default: false },
})

defineEmits(['close', 'view-task'])

const { formatFullDateTime, getStatusBadgeColor, getDeadlineTextColor } = useCalendarUtils()

const formatModalDate = (date) => {
  if (!date) return ''
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
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
