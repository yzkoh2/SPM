<template>
  <div>
    <!-- Calendar Navigation -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
      <div class="flex items-center justify-between mb-6">
        <button @click="previousMonth" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            ></path>
          </svg>
        </button>

        <div class="text-center">
          <h2 class="text-2xl font-bold text-gray-900">{{ currentMonthYear }}</h2>
          <p class="text-xs text-gray-500 mt-1">{{ subtitle }}</p>
          <button
            @click="goToToday"
            class="text-sm text-indigo-600 hover:text-indigo-700 font-medium mt-1"
          >
            Today
          </button>
        </div>

        <button @click="nextMonth" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            ></path>
          </svg>
        </button>
      </div>

      <!-- Filters Slot -->
      <div class="flex flex-wrap gap-3 mb-4">
        <slot name="filters"></slot>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="text-sm text-gray-500 mt-4">Loading tasks...</p>
      </div>

      <!-- Calendar Grid -->
      <div v-else class="grid grid-cols-7 gap-1">
        <!-- Day Headers -->
        <div
          v-for="day in weekDays"
          :key="day"
          class="text-center font-semibold text-sm text-gray-600 py-2"
        >
          {{ day }}
        </div>

        <!-- Calendar Days -->
        <div
          v-for="(day, index) in calendarDays"
          :key="index"
          @click="day.tasks.length > 0 && openDayModal(day)"
          :class="[
            'min-h-[120px] border border-gray-200 p-2 bg-white transition-all',
            day.isCurrentMonth ? '' : 'bg-gray-50',
            day.isToday ? 'ring-2 ring-indigo-500' : '',
            day.tasks.length > 0 ? 'hover:shadow-md cursor-pointer' : '',
          ]"
        >
          <div class="flex justify-between items-start mb-1">
            <span
              :class="[
                'text-sm font-medium',
                day.isToday
                  ? 'bg-indigo-600 text-white px-2 py-1 rounded-full'
                  : day.isCurrentMonth
                    ? 'text-gray-900'
                    : 'text-gray-400',
              ]"
            >
              {{ day.date.getDate() }}
            </span>
            <span
              v-if="day.tasks.length > 0"
              class="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium"
            >
              {{ day.tasks.length }}
            </span>
          </div>

          <div class="space-y-1 overflow-y-auto max-h-[80px]">
            <div
              v-for="task in day.tasks.slice(0, 2)"
              :key="task.id"
              @click.stop="$emit('view-task', task.id)"
              :class="[
                'text-xs p-1.5 rounded cursor-pointer hover:shadow-sm transition-all truncate',
                getTaskColorClass(task),
              ]"
            >
              <div class="font-medium truncate">{{ task.title }}</div>
              <div class="flex items-center gap-1 mt-0.5">
                <span
                  :class="[
                    'px-1.5 py-0.5 rounded text-[10px] font-medium',
                    getStatusBadgeColor(task.status),
                  ]"
                >
                  {{ task.status }}
                </span>
                <span class="text-[10px] text-gray-600">
                  {{ formatTimeOnly(task.deadline) }}
                </span>
              </div>
              <span
                v-if="!isPersonal && task.owner_name"
                class="text-[10px] font-medium text-purple-700 truncate max-w-[80px]"
              >
                Owner: {{ task.owner_name }}
              </span>
            </div>

            <div
              v-if="day.tasks.length > 2"
              @click.stop="openDayModal(day)"
              class="text-xs text-indigo-600 font-medium pl-1 hover:text-indigo-700 cursor-pointer"
            >
              +{{ day.tasks.length - 2 }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Summary -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
          <div class="p-2 bg-indigo-100 rounded-lg">
            <svg
              class="w-6 h-6 text-indigo-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              ></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Total Tasks</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stats.total }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Overdue</p>
            <p class="text-2xl font-semibold text-red-600">{{ stats.overdue }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
          <div class="p-2 bg-orange-100 rounded-lg">
            <svg
              class="w-6 h-6 text-orange-600"
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
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Due This Week</p>
            <p class="text-2xl font-semibold text-orange-600">{{ stats.dueThisWeek }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg
              class="w-6 h-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Completed</p>
            <p class="text-2xl font-semibold text-green-600">{{ stats.completed }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Day Modal -->
    <TaskDayModal
      v-if="showDayModal"
      :day="selectedDay"
      :show-owner-badge="showOwnerBadge"
      @close="closeDayModal"
      @view-task="$emit('view-task', $event)"
    />
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'
import TaskDayModal from './TaskDayModal.vue'
import { useCalendarUtils } from '@/composables/calendarUtils'

const props = defineProps({
  tasks: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  subtitle: { type: String, default: 'Times shown in your local timezone' },
  showOwnerBadge: { type: Boolean, default: false },
  isPersonal: { type: Boolean, default: false },
})

defineEmits(['view-task'])

const { convertToLocalTime, formatTimeOnly, getTaskColorClass, getStatusBadgeColor } =
  useCalendarUtils()

const currentDate = ref(new Date())
const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const showDayModal = ref(false)
const selectedDay = ref(null)

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  })
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const daysInMonth = lastDay.getDate()
  const startingDayOfWeek = firstDay.getDay()
  const prevMonthLastDay = new Date(year, month, 0).getDate()

  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // Previous month days
  for (let i = startingDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month - 1, prevMonthLastDay - i)
    days.push({ date, isCurrentMonth: false, isToday: false, tasks: getTasksForDate(date) })
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i)
    const dateOnly = new Date(date)
    dateOnly.setHours(0, 0, 0, 0)
    days.push({
      date,
      isCurrentMonth: true,
      isToday: dateOnly.getTime() === today.getTime(),
      tasks: getTasksForDate(date),
    })
  }

  // Next month days - only fill current week
  const daysInLastWeek = days.length % 7
  if (daysInLastWeek > 0) {
    const daysToAdd = 7 - daysInLastWeek
    for (let i = 1; i <= daysToAdd; i++) {
      const date = new Date(year, month + 1, i)
      days.push({ date, isCurrentMonth: false, isToday: false, tasks: getTasksForDate(date) })
    }
  }

  return days
})

const getTasksForDate = (date) => {
  const dateStr = date.toDateString()
  return props.tasks.filter((task) => {
    if (!task.deadline) return false
    return convertToLocalTime(task.deadline).toDateString() === dateStr
  })
}

const stats = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const now = new Date()
  const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

  return {
    total: props.tasks.filter((t) => {
      if (!t.deadline) return false
      const d = convertToLocalTime(t.deadline)
      return d.getFullYear() === year && d.getMonth() === month
    }).length,
    overdue: props.tasks.filter((t) => {
      if (!t.deadline || t.status === 'Completed') return false
      return convertToLocalTime(t.deadline) < now
    }).length,
    dueThisWeek: props.tasks.filter((t) => {
      if (!t.deadline || t.status === 'Completed') return false
      const d = convertToLocalTime(t.deadline)
      return d >= now && d <= weekFromNow
    }).length,
    completed: props.tasks.filter((t) => {
      if (t.status !== 'Completed' || !t.deadline) return false
      const d = convertToLocalTime(t.deadline)
      return d.getFullYear() === year && d.getMonth() === month
    }).length,
  }
})

const previousMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

const goToToday = () => {
  currentDate.value = new Date()
}

const openDayModal = (day) => {
  selectedDay.value = day
  showDayModal.value = true
}

const closeDayModal = () => {
  showDayModal.value = false
  selectedDay.value = null
}
</script>
