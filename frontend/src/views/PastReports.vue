<template>
  <div>
    <div class="bg-white shadow rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">Report Category</label>
          <select
            v-model="filterCategory"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Categories</option>
            <option value="project">Project Reports</option>
            <option value="individual">Individual Reports</option>
          </select>
        </div>

        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            {{ dynamicFilterLabel }}
          </label>
          <select
            v-model="filterTargetId"
            :disabled="!filterCategory"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
          >
            <option value="">{{ dynamicFilterAllText }}</option>
            <option v-for="option in dynamicFilterOptions" :key="option.id" :value="option.id">
              {{ option.name }}
            </option>
          </select>
        </div>
        
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
          <select
            v-model="sortOrder"
            @change="sortReports"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
        </div>

      </div>
    </div>
    <div v-if="loading" class="text-center py-12">
      <div
        class="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"
      ></div>
      <p class="mt-4 text-gray-600">Loading reports...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 text-red-700">
      {{ error }}
    </div>

    <div
      v-else-if="filteredReports.length === 0"
      class="text-center py-12 bg-white shadow rounded-lg"
    >
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        ></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No reports found</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ filterCategory ? 'No reports match your filter.' : 'Generate your first report to see it here.' }}
      </p>
    </div>

    <div v-else class="bg-white shadow rounded-lg overflow-hidden">
      <ul class="divide-y divide-gray-200">
        <li v-for="report in filteredReports" :key="report.id" class="hover:bg-gray-50">
          <div class="px-6 py-4">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-2">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      report.report_type === 'project'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800',
                    ]"
                  >
                    {{ report.report_type === 'project' ? 'Project' : 'Individual' }}
                  </span>
                </div>

                <h3 class="text-lg font-semibold text-indigo-700 truncate">
                  {{ report.target_name || 'General Report' }}
                </h3>

                <p class="text-sm font-medium text-gray-700 truncate">{{ report.filename }}</p>

                <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
                  <span class="flex items-center">
                    <svg
                      class="mr-1.5 h-4 w-4 text-gray-400"
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
                    {{ formatDate(report.created_at) }}
                  </span>

                  <span v-if="report.file_size" class="flex items-center">
                    <svg
                      class="mr-1.5 h-4 w-4 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                      ></path>
                    </svg>
                    {{ formatFileSize(report.file_size) }}
                  </span>
                </div>
              </div>

              <div class="ml-4 flex items-center gap-2">
                <button
                  @click="previewReport(report.id, report.file_name)"
                  :disabled="downloading === report.id"
                  class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                <svg
                    v-if="downloading !== report.id"
                    class="h-4 w-4 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                  <div
                    v-else
                    class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700 mr-1"
                  ></div>
                  View
                </button>

                <button
                  @click="confirmDelete(report)"
                  class="inline-flex items-center p-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          </div>
        </li>
      </ul>
    </div>

    <div v-if="showDeleteModal" class="fixed z-50 inset-0 overflow-y-auto">
      <div
        class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"
      >
        <div
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          @click="showDeleteModal = false"
          aria-hidden="true"
        ></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true"
          >&#8203;</span
        >
        <div
          class="relative inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
        >
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div
                class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
              >
                <svg
                  class="h-6 w-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  ></path>
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900">Delete Report</h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Are you sure you want to delete this report? This action cannot be undone.
                  </p>
                  <p class="mt-2 text-sm font-medium text-gray-700">
                    {{ reportToDelete?.filename }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              @click="deleteReport"
              :disabled="deleting"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
            >
              {{ deleting ? 'Deleting...' : 'Delete' }}
            </button>
            <button
              type="button"
              @click="showDeleteModal = false"
              :disabled="deleting"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const KONG_API_URL = 'http://localhost:8000'

// State
const reports = ref([]) // This holds ALL reports fetched from the API
const loading = ref(true)
const error = ref(null)
const sortOrder = ref('desc') // For sorting
const downloading = ref(null)
const showDeleteModal = ref(false)
const reportToDelete = ref(null)
const deleting = ref(false)

// --- Revamped Filter State ---
const filterCategory = ref('') // Holds: '', 'project', 'individual'
const filterTargetId = ref('') // Holds: '', project_id, target_user_id

// --- Watcher ---
// This resets the second filter (filterTargetId) whenever the first filter (filterCategory) changes.
watch(filterCategory, () => {
  filterTargetId.value = ''
})

// --- Computed Properties for Filters ---

// Populates the second dropdown based on the first dropdown's selection
const dynamicFilterOptions = computed(() => {
  const options = new Map()

  if (filterCategory.value === 'project') {
    reports.value.forEach(r => {
      // Use project_id as the key to de-duplicate
      if (r.report_type === 'project' && r.project_id && r.target_name) {
        options.set(r.project_id, r.target_name)
      }
    })
  } else if (filterCategory.value === 'individual') {
    reports.value.forEach(r => {
      // Use target_user_id as the key to de-duplicate
      if (r.report_type === 'individual' && r.target_user_id && r.target_name) {
        options.set(r.target_user_id, r.target_name)
      }
    })
  }
  
  // Convert the Map(id, name) into an array [{id, name}] and sort it by name
  return Array.from(options, ([id, name]) => ({ id, name }))
    .sort((a, b) => a.name.localeCompare(b.name))
})

// Computes the label for the second dropdown
const dynamicFilterLabel = computed(() => {
  if (filterCategory.value === 'project') return 'Project'
  if (filterCategory.value === 'individual') return 'User'
  return 'Specific Target'
})

// Computes the "All" text for the second dropdown
const dynamicFilterAllText = computed(() => {
  if (filterCategory.value === 'project') return 'All Projects'
  if (filterCategory.value === 'individual') return 'All Users'
  return 'All'
})

// The main computed property that performs all filtering
const filteredReports = computed(() => {
  // Start with the full list of reports
  let baseReports = reports.value

  // 1. Filter by Category
  const categoryFiltered = !filterCategory.value
    ? baseReports // No category selected, show all
    : baseReports.filter(r => r.report_type === filterCategory.value)

  // 2. Filter by Specific Target
  // This only runs if filterTargetId has a value (i.e., not 'All Projects' or 'All Users')
  if (!filterTargetId.value) {
    return categoryFiltered // No specific target, return the category-filtered list
  }

  // We already know the category from filterCategory, so we check the corresponding ID
  if (filterCategory.value === 'project') {
    return categoryFiltered.filter(r => r.project_id === filterTargetId.value)
  }

  if (filterCategory.value === 'individual') {
    return categoryFiltered.filter(r => r.target_user_id === filterTargetId.value)
  }

  return categoryFiltered // Fallback
})

// --- Methods ---

const loadReports = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await fetch(
      `${KONG_API_URL}/reports/history/${authStore.user.id}`,
    )

    if (!response.ok) {
      throw new Error('Failed to load reports')
    }

    const data = await response.json()
    reports.value = data
    sortReports() // Apply initial sort
  } catch (err) {
    console.error('Error loading reports:', err)
    error.value = err.message || 'Failed to load reports'
  } finally {
    loading.value = false
  }
}

// Sorts the *base* reports array. filteredReports will auto-update.
const sortReports = () => {
  reports.value.sort((a, b) => {
    const dateA = new Date(a.created_at)
    const dateB = new Date(b.created_at)
    return sortOrder.value === 'desc' ? dateB - dateA : dateA - dateB
  })
}

const previewReport = async (reportId) => {
  downloading.value = reportId
  try {
    const response = await fetch(
      `${KONG_API_URL}/reports/retrieve/${reportId}?user_id=${authStore.user.id}`,
    )
    if (!response.ok) {
      throw new Error('Failed to download report')
    }
    const data = await response.json()
    const presignedUrl = data.url
    window.open(presignedUrl, '_blank')
  } catch (err) {
    console.error('Error downloading report:', err)
    alert('Failed to download report. Please try again.')
  } finally {
    downloading.value = null
  }
}

const confirmDelete = (report) => {
  reportToDelete.value = report
  showDeleteModal.value = true
}

const deleteReport = async () => {
  deleting.value = true
  try {
    const response = await fetch(
      `${KONG_API_URL}/reports/delete/${reportToDelete.value.id}?user_id=${authStore.user.id}`,
      {
        method: 'DELETE',
      },
    )
    if (!response.ok) {
      throw new Error('Failed to delete report')
    }
    reports.value = reports.value.filter((r) => r.id !== reportToDelete.value.id)
    showDeleteModal.value = false
    reportToDelete.value = null
  } catch (err) {
    console.error('Error deleting report:', err)
    alert('Failed to delete report. Please try again.')
  } finally {
    deleting.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// Lifecycle
onMounted(() => {
  if (authStore.isAuthenticated) {
    loadReports()
  } else {
    authStore.logout()
  }
})
</script>