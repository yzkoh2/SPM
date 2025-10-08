<template>
    <div>
      <!-- Calendar Navigation -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div class="flex items-center justify-between mb-6">
          <button @click="previousMonth" 
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          
          <div class="text-center">
            <h2 class="text-2xl font-bold text-gray-900">{{ currentMonthYear }}</h2>
            <p class="text-xs text-gray-500 mt-1">Times shown in your local timezone</p>
            <button @click="goToToday" 
              class="text-sm text-indigo-600 hover:text-indigo-700 font-medium mt-1">
              Today
            </button>
          </div>
          
          <button @click="nextMonth" 
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
  
        <!-- Filter Options -->
        <div class="flex flex-wrap gap-3 mb-4">
          <button @click="filters.showOwned = !filters.showOwned"
            :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                     filters.showOwned ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200']">
            My Tasks
          </button>
          <button @click="filters.showCollaborating = !filters.showCollaborating"
            :class="['px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                     filters.showCollaborating ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200']">
            Collaborating
          </button>
          <select v-model="filters.status" 
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="">All Statuses</option>
            <option value="Unassigned">Unassigned</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Under Review">Under Review</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
  
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p class="text-sm text-gray-500 mt-4">Loading your tasks...</p>
        </div>
  
        <!-- Calendar Grid -->
        <div v-else class="grid grid-cols-7 gap-1">
          <!-- Day Headers -->
          <div v-for="day in weekDays" :key="day" 
            class="text-center font-semibold text-sm text-gray-600 py-2">
            {{ day }}
          </div>
  
          <!-- Calendar Days -->
          <div v-for="(day, index) in calendarDays" :key="index"
            @click="day.tasks.length > 0 && openDayModal(day)"
            :class="['min-h-[120px] border border-gray-200 p-2 bg-white transition-all',
                     day.isCurrentMonth ? '' : 'bg-gray-50',
                     day.isToday ? 'ring-2 ring-indigo-500' : '',
                     day.tasks.length > 0 ? 'hover:shadow-md cursor-pointer' : '']">
            
            <!-- Day Number -->
            <div class="flex justify-between items-start mb-1">
              <span :class="['text-sm font-medium',
                             day.isToday ? 'bg-indigo-600 text-white px-2 py-1 rounded-full' : 
                             day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400']">
                {{ day.date.getDate() }}
              </span>
              <span v-if="day.tasks.length > 0" 
                class="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
                {{ day.tasks.length }}
              </span>
            </div>
  
            <!-- Tasks for this day (compact view) -->
            <div class="space-y-1 overflow-y-auto max-h-[80px]">
              <div v-for="task in day.tasks.slice(0, 2)" :key="task.id"
                @click.stop="viewTaskDetails(task.id)"
                :class="['text-xs p-1.5 rounded cursor-pointer hover:shadow-sm transition-all truncate',
                         getTaskColorClass(task)]">
                <div class="font-medium truncate">{{ task.title }}</div>
                <div class="flex items-center gap-1 mt-0.5">
                  <span :class="['px-1.5 py-0.5 rounded text-[10px] font-medium',
                                 getStatusBadgeColor(task.status)]">
                    {{ task.status }}
                  </span>
                  <span class="text-[10px] text-gray-600">
                    {{ formatTimeOnly(task.deadline) }}
                  </span>
                </div>
              </div>
              
              <!-- More tasks indicator -->
              <div v-if="day.tasks.length > 2" 
                @click.stop="openDayModal(day)"
                class="text-xs text-indigo-600 font-medium pl-1 hover:text-indigo-700 cursor-pointer">
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
              <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Tasks</p>
              <p class="text-2xl font-semibold text-gray-900">{{ totalTasksThisMonth }}</p>
            </div>
          </div>
        </div>
  
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-red-100 rounded-lg">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Overdue</p>
              <p class="text-2xl font-semibold text-red-600">{{ overdueTasksCount }}</p>
            </div>
          </div>
        </div>
  
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-orange-100 rounded-lg">
              <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Due This Week</p>
              <p class="text-2xl font-semibold text-orange-600">{{ dueThisWeekCount }}</p>
            </div>
          </div>
        </div>
  
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Completed</p>
              <p class="text-2xl font-semibold text-green-600">{{ completedTasksCount }}</p>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Day Tasks Modal -->
      <div v-if="showDayModal" 
        @click="closeDayModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div @click.stop 
          class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
          <!-- Modal Header -->
          <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-4 flex justify-between items-center">
            <div>
              <h3 class="text-xl font-bold text-white">
                {{ formatModalDate(selectedDay?.date) }}
              </h3>
              <p class="text-indigo-100 text-sm mt-1">
                {{ selectedDay?.tasks.length }} {{ selectedDay?.tasks.length === 1 ? 'task' : 'tasks' }}
              </p>
            </div>
            <button @click="closeDayModal" 
              class="text-white hover:bg-indigo-500 rounded-lg p-2 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
  
          <!-- Modal Body -->
          <div class="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
            <div class="space-y-4">
              <div v-for="task in selectedDay?.tasks" :key="task.id"
                class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer"
                @click="viewTaskDetails(task.id)">
                
                <!-- Task Header -->
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <h4 class="font-semibold text-gray-900 text-lg">{{ task.title }}</h4>
                    <div class="flex items-center gap-2 mt-2">
                      <span :class="['px-3 py-1 rounded-full text-xs font-medium',
                                     getStatusBadgeColor(task.status)]">
                        {{ task.status }}
                      </span>
                      <span v-if="task.is_owner" 
                        class="px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        Owner
                      </span>
                      <span v-else
                        class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Collaborator
                      </span>
                    </div>
                  </div>
                  <svg class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </div>
  
                <!-- Task Details -->
                <div class="space-y-2 text-sm text-gray-600">
                  <div v-if="task.description" class="flex items-start">
                    <svg class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M4 6h16M4 12h16M4 18h7"></path>
                    </svg>
                    <p class="line-clamp-2">{{ task.description }}</p>
                  </div>
                  
                  <div class="flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span :class="getDeadlineTextColor(task.deadline)">
                      {{ formatFullDateTime(task.deadline) }}
                    </span>
                  </div>
  
                  <div v-if="task.project_id" class="flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                    </svg>
                    <span>Part of project ID: {{ task.project_id }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Modal Footer -->
          <div class="bg-gray-50 px-6 py-4 flex justify-end">
            <button @click="closeDayModal"
              class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  
  const router = useRouter()
  const authStore = useAuthStore()
  
  // API configuration
  const KONG_API_URL = "http://localhost:8000"
  
  // Reactive data
  const currentDate = ref(new Date())
  const tasks = ref([])
  const loading = ref(true)
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const showDayModal = ref(false)
  const selectedDay = ref(null)
  
  // Filters
  const filters = ref({
    showOwned: true,
    showCollaborating: true,
    status: ''
  })
  
  // Timezone conversion helper
  const convertToLocalTime = (utcTimestamp) => {
    if (!utcTimestamp) return null
    let dateStr = utcTimestamp
    if (!dateStr.includes('Z') && !dateStr.includes('+')) {
      dateStr = dateStr + 'Z'
    }
    return new Date(dateStr)
  }
  
  // Computed properties
  const currentMonthYear = computed(() => {
    return currentDate.value.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    })
  })
  
  const calendarDays = computed(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    const firstDay = new Date(year, month, 1)
    const startingDayOfWeek = firstDay.getDay()
    
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    
    const prevMonthLastDay = new Date(year, month, 0).getDate()
    
    const days = []
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month - 1, prevMonthLastDay - i)
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        tasks: getTasksForDate(date)
      })
    }
    
    for (let i = 1; i <= daysInMonth; i++) {
      const date = new Date(year, month, i)
      const dateOnly = new Date(date)
      dateOnly.setHours(0, 0, 0, 0)
      
      days.push({
        date,
        isCurrentMonth: true,
        isToday: dateOnly.getTime() === today.getTime(),
        tasks: getTasksForDate(date)
      })
    }
    
    const remainingDays = 42 - days.length
    for (let i = 1; i <= remainingDays; i++) {
      const date = new Date(year, month + 1, i)
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        tasks: getTasksForDate(date)
      })
    }
    
    return days
  })
  
  const filteredTasks = computed(() => {
    let filtered = [...tasks.value]
    
    if (!filters.value.showOwned) {
      filtered = filtered.filter(task => !task.is_owner)
    }
    if (!filters.value.showCollaborating) {
      filtered = filtered.filter(task => task.is_owner)
    }
    
    if (filters.value.status) {
      filtered = filtered.filter(task => task.status === filters.value.status)
    }
    
    return filtered
  })
  
  const totalTasksThisMonth = computed(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    return filteredTasks.value.filter(task => {
      if (!task.deadline) return false
      const deadline = convertToLocalTime(task.deadline)
      return deadline.getFullYear() === year && deadline.getMonth() === month
    }).length
  })
  
  const overdueTasksCount = computed(() => {
    const now = new Date()
    return filteredTasks.value.filter(task => {
      if (!task.deadline || task.status === 'Completed') return false
      return convertToLocalTime(task.deadline) < now
    }).length
  })
  
  const dueThisWeekCount = computed(() => {
    const now = new Date()
    const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
    
    return filteredTasks.value.filter(task => {
      if (!task.deadline || task.status === 'Completed') return false
      const deadline = convertToLocalTime(task.deadline)
      return deadline >= now && deadline <= weekFromNow
    }).length
  })
  
  const completedTasksCount = computed(() => {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    return filteredTasks.value.filter(task => {
      if (task.status !== 'Completed' || !task.deadline) return false
      const deadline = convertToLocalTime(task.deadline)
      return deadline.getFullYear() === year && deadline.getMonth() === month
    }).length
  })
  
  // Methods
  const getTasksForDate = (date) => {
    const dateStr = date.toDateString()
    return filteredTasks.value.filter(task => {
      if (!task.deadline) return false
      const taskDeadline = convertToLocalTime(task.deadline)
      return taskDeadline.toDateString() === dateStr
    })
  }
  
  const getTaskColorClass = (task) => {
    const now = new Date()
    const deadline = convertToLocalTime(task.deadline)
    
    if (task.status === 'Completed') {
      return 'bg-green-100 border-l-4 border-green-500 text-green-800'
    } else if (deadline < now) {
      return 'bg-red-100 border-l-4 border-red-500 text-red-800'
    } else if (task.is_owner) {
      return 'bg-indigo-100 border-l-4 border-indigo-500 text-indigo-800'
    } else {
      return 'bg-green-50 border-l-4 border-green-400 text-green-700'
    }
  }
  
  const getStatusBadgeColor = (status) => {
    const colors = {
      'Unassigned': 'bg-gray-100 text-gray-800',
      'Ongoing': 'bg-blue-100 text-blue-800',
      'Under Review': 'bg-yellow-100 text-yellow-800',
      'Completed': 'bg-green-100 text-green-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }
  
  const getDeadlineTextColor = (deadline) => {
    if (!deadline) return 'text-gray-600'
    
    const now = new Date()
    const deadlineDate = convertToLocalTime(deadline)
    
    if (deadlineDate < now) return 'text-red-600 font-semibold'
    if (deadlineDate.toDateString() === now.toDateString()) return 'text-orange-600 font-semibold'
    return 'text-gray-700'
  }
  
  const formatTimeOnly = (deadline) => {
    if (!deadline) return ''
    const date = convertToLocalTime(deadline)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }
  
  const formatFullDateTime = (deadline) => {
    if (!deadline) return 'No deadline'
    const date = convertToLocalTime(deadline)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }
  
  const formatModalDate = (date) => {
    if (!date) return ''
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
  
  const fetchTasks = async () => {
    try {
      loading.value = true
      const userId = authStore.currentUserId
      
      const ownerResponse = await fetch(`${KONG_API_URL}/tasks?owner_id=${userId}`)
      const ownerTasks = await ownerResponse.json()
      
      const collabResponse = await fetch(`${KONG_API_URL}/tasks?collaborator_id=${userId}`)
      const collabTasks = await collabResponse.json()
      
      const allTasks = [
        ...ownerTasks.map(task => ({ ...task, is_owner: true })),
        ...collabTasks.map(task => ({ ...task, is_owner: false }))
      ]
      
      const uniqueTasks = allTasks.filter((task, index, self) =>
        index === self.findIndex(t => t.id === task.id)
      )
      
      tasks.value = uniqueTasks
    } catch (error) {
      console.error('Error fetching tasks:', error)
    } finally {
      loading.value = false
    }
  }
  
  const previousMonth = () => {
    currentDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth() - 1,
      1
    )
  }
  
  const nextMonth = () => {
    currentDate.value = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth() + 1,
      1
    )
  }
  
  const goToToday = () => {
    currentDate.value = new Date()
  }
  
  const viewTaskDetails = (taskId) => {
    router.push(`/tasks/${taskId}`)
  }
  
  const openDayModal = (day) => {
    selectedDay.value = day
    showDayModal.value = true
  }
  
  const closeDayModal = () => {
    showDayModal.value = false
    selectedDay.value = null
  }
  
  onMounted(() => {
    fetchTasks()
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