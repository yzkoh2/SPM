<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Generate Performance Report</h1>
        <p class="text-sm text-gray-600 mt-1">
          Create individual or project task performance reports
        </p>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-red-700 text-sm">{{ error }}</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loadingUser" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Main Form Card -->
      <div v-else class="bg-white rounded-lg shadow-md p-6">
        <form @submit.prevent="generateReport">
          <!-- Report Type Selection -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-3">Report Type</label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button type="button" @click="reportType = 'individual'" :class="[
                'p-4 border-2 rounded-lg transition-all',
                reportType === 'individual'
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-300 hover:border-gray-400',
              ]">
                <div class="flex items-center">
                  <div :class="[
                    'w-5 h-5 rounded-full border-2 flex items-center justify-center mr-3',
                    reportType === 'individual' ? 'border-indigo-600' : 'border-gray-300',
                  ]">
                    <div v-if="reportType === 'individual'" class="w-3 h-3 rounded-full bg-indigo-600"></div>
                  </div>
                  <div class="text-left">
                    <p class="font-medium text-gray-900">Individual Report</p>
                    <p class="text-xs text-gray-500">Personal task performance metrics</p>
                  </div>
                </div>
              </button>

              <button type="button" @click="reportType = 'project'" :class="[
                'p-4 border-2 rounded-lg transition-all',
                reportType === 'project'
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-300 hover:border-gray-400',
              ]">
                <div class="flex items-center">
                  <div :class="[
                    'w-5 h-5 rounded-full border-2 flex items-center justify-center mr-3',
                    reportType === 'project' ? 'border-indigo-600' : 'border-gray-300',
                  ]">
                    <div v-if="reportType === 'project'" class="w-3 h-3 rounded-full bg-indigo-600"></div>
                  </div>
                  <div class="text-left">
                    <p class="font-medium text-gray-900">Project Report</p>
                    <p class="text-xs text-gray-500">Team project performance metrics</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Individual Report Options -->
          <div v-if="reportType === 'individual'" class="space-y-6">
            <!-- User Selection (for Managers and Directors) -->
            <div v-if="canSelectOtherUsers">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Select User
                <span class="text-red-500">*</span>
              </label>
              <select v-model="selectedUserId" required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">-- Select a user --</option>
                <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                  {{ user.name }} ({{ user.role }})
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">
                <span v-if="currentUser.role === 'Manager'">You can generate reports for your team members</span>
                <span v-else-if="currentUser.role === 'Director'">You can generate reports for your department
                  members</span>
              </p>
            </div>

            <div v-else>
              <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p class="text-sm text-blue-700">
                  <span class="font-medium">Generating report for:</span>
                  {{ currentUser?.name || 'Current User' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Project Report Options -->
          <div v-if="reportType === 'project'" class="space-y-6">
            <!-- Project Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Select Project
                <span class="text-red-500">*</span>
              </label>
              <select v-model="selectedProjectId" required :disabled="loadingProjects"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100">
                <option value="">-- Select a project --</option>
                <option v-for="project in userProjects" :key="project.id" :value="project.id">
                  {{ project.title }}
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">Select a project you own or collaborate on</p>
            </div>
          </div>

          <!-- Timeframe Selection (Common for both types) -->
          <div class="mt-6 space-y-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Timeframe
              <span class="text-red-500">*</span>
            </label>

            <!-- Predefined Timeframes -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button type="button" @click="selectTimeframe('this_month')" :class="[
                'px-4 py-2 border rounded-md text-sm font-medium transition-colors',
                timeframe === 'this_month'
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
              ]">
                This Month
              </button>

              <button type="button" @click="selectTimeframe('last_month')" :class="[
                'px-4 py-2 border rounded-md text-sm font-medium transition-colors',
                timeframe === 'last_month'
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
              ]">
                Last Month
              </button>

              <button type="button" @click="selectTimeframe('last_3_months')" :class="[
                'px-4 py-2 border rounded-md text-sm font-medium transition-colors',
                timeframe === 'last_3_months'
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
              ]">
                Last 3 Months
              </button>

              <button type="button" @click="selectTimeframe('custom')" :class="[
                'px-4 py-2 border rounded-md text-sm font-medium transition-colors',
                timeframe === 'custom'
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
              ]">
                Custom Range
              </button>
            </div>

            <!-- Custom Date Range -->
            <div v-if="timeframe === 'custom'"
              class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 p-4 bg-gray-50 rounded-md">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                <input type="date" v-model="customStartDate" required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                <input type="date" v-model="customEndDate" required :min="customStartDate"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              </div>
            </div>

            <!-- Selected Timeframe Display -->
            <div v-if="timeframe && timeframe !== 'custom'" class="text-sm text-gray-600">
              <span class="font-medium">Selected period:</span> {{ getTimeframeDisplay() }}
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-8 flex justify-end space-x-3">
            <button type="button" @click="resetForm"
              class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
              Reset
            </button>
            <button type="submit" :disabled="isGenerating || !isFormValid"
              class="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center">
              <svg v-if="isGenerating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none"
                viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                </path>
              </svg>
              {{ isGenerating ? 'Generating...' : 'Generate Report' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Info Box -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
        <div class="flex">
          <svg class="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div class="text-sm text-blue-700">
            <p class="font-medium mb-1">Report Information:</p>
            <ul class="list-disc list-inside space-y-1 text-xs">
              <li>Reports are generated in PDF format and will download automatically</li>
              <li>Individual reports show personal task performance metrics</li>
              <li>Project reports show team performance across all project tasks</li>
              <li>
                Reports include completion rates, average completion time, and velocity metrics
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import TaskboardNavigation from '@/components/TaskboardNavigation.vue'

const authStore = useAuthStore()

// API Configuration
const KONG_API_URL = 'http://localhost:8000'

// Reactive data
const reportType = ref('individual')
const currentUser = ref(null)
const availableUsers = ref([])
const selectedUserId = ref('')
const userProjects = ref([])
const selectedProjectId = ref('')
const timeframe = ref('')
const customStartDate = ref('')
const customEndDate = ref('')
const isGenerating = ref(false)
const loadingProjects = ref(false)
const loadingUser = ref(true)
const error = ref(null)

// Computed properties
const canSelectOtherUsers = computed(() => {
  return (
    currentUser.value &&
    (currentUser.value.role === 'Manager' || currentUser.value.role === 'Director')
  )
})

const isFormValid = computed(() => {
  if (!timeframe.value) return false

  if (timeframe.value === 'custom') {
    if (!customStartDate.value || !customEndDate.value) return false
  }

  if (reportType.value === 'individual') {
    if (canSelectOtherUsers.value && !selectedUserId.value) return false
    return true
  }

  if (reportType.value === 'project') {
    return !!selectedProjectId.value
  }

  return false
})

// Methods
const fetchCurrentUser = async () => {
  try {
    loadingUser.value = true
    const response = await fetch(`${KONG_API_URL}/user/${authStore.user.id}`)
    if (!response.ok) throw new Error('Failed to fetch user details')
    currentUser.value = await response.json()
    selectedUserId.value = currentUser.value.id
    console.log('Current user details:', currentUser.value)

    // Fetch appropriate users based on role
    if (currentUser.value.role === 'Manager') {
      await fetchTeamMembers()
    } else if (currentUser.value.role === 'Director') {
      await fetchDepartmentMembers()
    }
  } catch (err) {
    console.error('Error fetching current user:', err)
    error.value = 'Failed to load user information'
  } finally {
    loadingUser.value = false
  }
}

const fetchTeamMembers = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/user/team/${currentUser.value.team_id}`)
    if (!response.ok) throw new Error('Failed to fetch team members')
    availableUsers.value = await response.json()
  } catch (err) {
    console.error('Error fetching team members:', err)
    error.value = 'Failed to load team members'
  }
}

const fetchDepartmentMembers = async () => {
  try {
    console.log('Fetching department members for department ID:', currentUser.value.department_id)
    const response = await fetch(
      `${KONG_API_URL}/user/department/${currentUser.value.department_id}`,
    )
    if (!response.ok) throw new Error('Failed to fetch department members')
    availableUsers.value = await response.json()
  } catch (err) {
    console.error('Error fetching department members:', err)
    error.value = 'Failed to load department members'
  }
}

const fetchUserProjects = async () => {
  loadingProjects.value = true
  try {
    const response = await fetch(`${KONG_API_URL}/projects/user/${authStore.user.id}`)
    if (!response.ok) throw new Error('Failed to fetch projects')
    userProjects.value = await response.json()
    console.log('Fetched user projects:', userProjects.value)
  } catch (err) {
    console.error('Error fetching projects:', err)
    error.value = 'Failed to load projects'
  } finally {
    loadingProjects.value = false
  }
}

const selectTimeframe = (period) => {
  timeframe.value = period
  if (period !== 'custom') {
    customStartDate.value = ''
    customEndDate.value = ''
  }
}

const getTimeframeDisplay = () => {
  const now = new Date()

  switch (timeframe.value) {
    case 'this_month':
      return `${now.toLocaleString('default', { month: 'long' })} ${now.getFullYear()}`
    case 'last_month': {
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
      return `${lastMonth.toLocaleString('default', { month: 'long' })} ${lastMonth.getFullYear()}`
    }
    case 'last_3_months': {
      const threeMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 2, 1)
      return `${threeMonthsAgo.toLocaleString('default', { month: 'short' })} - ${now.toLocaleString('default', { month: 'short' })} ${now.getFullYear()}`
    }
    default:
      return ''
  }
}

const calculateDateRange = () => {
  if (timeframe.value === 'custom') {
    return {
      start_date: customStartDate.value,
      end_date: customEndDate.value,
    }
  }

  const now = new Date()
  let startDate, endDate

  switch (timeframe.value) {
    case 'this_month':
      startDate = new Date(now.getFullYear(), now.getMonth(), 1)
      endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      break
    case 'last_month':
      startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
      endDate = new Date(now.getFullYear(), now.getMonth(), 0)
      break
    case 'last_3_months':
      startDate = new Date(now.getFullYear(), now.getMonth() - 2, 1)
      endDate = now
      break
    default:
      return {}
  }

  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
  }
}

const generateReport = async () => {
  error.value = null
  isGenerating.value = true

  try {
    const dateRange = calculateDateRange()
    let endpoint, payload

    if (reportType.value === 'individual') {
      endpoint = `${KONG_API_URL}/reports/individual`
      payload = {
        user_id: selectedUserId.value || currentUser.value.id,
        requester_id: authStore.user.id,
        ...dateRange,
      }
    } else {
      if (!selectedProjectId.value) throw new Error('Please select a project.')

      // Construct URL with user_id as query param
      const endpoint = `${KONG_API_URL}/reports/project/${selectedProjectId.value}?user_id=${authStore.user.id}`

      // JSON body for dates and timezone
      const payload = {
        start_date: dateRange.start_date || null,
        end_date: dateRange.end_date || null,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC', // user's browser timezone
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to generate project report')
      }

      // Handle PDF download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ProjectTaskPerformanceReport_${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      alert('Project report generated successfully!')
      resetForm()
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to generate report')
    }

    // Handle PDF download
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url

    const fileName =
      reportType.value === 'individual'
        ? `IndividualTaskPerformanceReport_${new Date().toISOString().split('T')[0]}.pdf`
        : `ProjectTaskPerformanceReport_${new Date().toISOString().split('T')[0]}.pdf`

    a.download = fileName
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    // Show success message
    alert('Report generated successfully!')
    resetForm()
  } catch (err) {
    console.error('Error generating report:', err)
    error.value = err.message || 'Failed to generate report. Please try again.'
  } finally {
    isGenerating.value = false
  }
}

const resetForm = () => {
  if (canSelectOtherUsers.value) {
    selectedUserId.value = ''
  } else {
    selectedUserId.value = currentUser.value?.id || ''
  }
  selectedProjectId.value = ''
  timeframe.value = ''
  customStartDate.value = ''
  customEndDate.value = ''
  error.value = null
}

// Lifecycle hooks
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await fetchCurrentUser()
    await fetchUserProjects()
  } else {
    authStore.logout()
  }
})
</script>
