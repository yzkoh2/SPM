<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">My Projects</h1>
        <p class="text-sm text-gray-600 mt-1">Manage your projects and collaborate with your team</p>
      </div>

      <!-- Create Button -->
      <div class="mb-6">
        <button
          @click="showCreateForm = !showCreateForm"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            ></path>
          </svg>
          {{ showCreateForm ? 'Cancel' : 'Create New Project' }}
        </button>
      </div>

      <!-- Create Project Form -->
      <div v-if="showCreateForm" class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Create New Project</h3>
        <form @submit.prevent="createProject">
          <div class="grid grid-cols-1 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Project Title *</label>
              <input
                v-model="newProject.title"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter project title"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea
                v-model="newProject.description"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter project description"
                required
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline *</label>
              <input
                v-model="newProject.deadline"
                type="datetime-local"
                :min="minDeadline"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                required
              />
            </div>

            <!-- Collaborator Management Section -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2"
                >Manage Collaborators</label
              >

              <!-- Added Collaborators List -->
              <div
                class="space-y-2 mb-4 max-h-40 overflow-y-auto p-2 border border-gray-200 rounded-md bg-gray-50"
              >
                <div
                  v-if="localCollaborators.length === 0"
                  class="text-sm text-gray-500 text-center py-2"
                >
                  No collaborators added yet.
                </div>
                <div
                  v-for="collaborator in localCollaborators"
                  :key="collaborator.user_id"
                  class="flex items-center justify-between p-2 bg-white rounded-md shadow-sm border border-gray-100"
                >
                  <span class="text-sm font-medium text-gray-800"
                    >{{ collaborator.name }} ({{ collaborator.role }})</span
                  >
                  <button
                    @click="removeCollaborator(collaborator.user_id)"
                    type="button"
                    title="Remove Collaborator"
                    class="text-red-500 hover:text-red-700 text-xs font-semibold p-1 rounded-full hover:bg-red-50 transition"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      ></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Collaborator Filters -->
              <div class="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <label class="block text-xs text-gray-500">Filter by Department</label>
                  <select
                    v-model="collaboratorDepartmentFilter"
                    class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                  >
                    <option value="">All Departments</option>
                    <option v-for="dept in collaboratorDepartments" :key="dept" :value="dept">
                      {{ dept }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs text-gray-500">Filter by Role</label>
                  <select
                    v-model="collaboratorRoleFilter"
                    class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                  >
                    <option value="">All Roles</option>
                    <option v-for="role in collaboratorRoles" :key="role" :value="role">
                      {{ role }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Collaborator Add Input -->
              <div class="flex items-center space-x-2">
                <select
                  v-model="selectedCollaboratorId"
                  class="flex-grow border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
                >
                  <option :value="null" disabled>
                    Select a user to add ({{ availableCollaborators.length }} available)...
                  </option>
                  <option v-for="user in availableCollaborators" :key="user.id" :value="user.id">
                    {{ user.name }} ({{ user.department }} - {{ user.role }})
                  </option>
                </select>
                <button
                  @click="addCollaborator"
                  type="button"
                  :disabled="!selectedCollaboratorId"
                  class="flex-shrink-0 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-md text-sm font-medium disabled:opacity-50 transition duration-150"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
          <div class="mt-4 flex justify-end space-x-3">
            <button
              type="button"
              @click="showCreateForm = false"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isCreating"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400"
            >
              {{ isCreating ? 'Creating...' : 'Create Project' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Filter and Sort Bar -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <div
          class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0"
        >
          <div
            class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4"
          >
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Role</label>
              <select
                v-model="filters.role"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Projects</option>
                <option value="owner">My Projects</option>
                <option value="collaborator">Collaborating</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sort by</label>
              <select
                v-model="sortBy"
                @change="applyFilters"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="default">Default Order</option>
                <option value="deadline-earliest">Deadline (Earliest First)</option>
                <option value="deadline-latest">Deadline (Latest First)</option>
                <option value="title-asc">Title (A-Z)</option>
                <option value="title-desc">Title (Z-A)</option>
              </select>
            </div>
          </div>

          <div
            class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4"
          >
            <button
              @click="clearFilters"
              class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              Clear Filters
            </button>
            <button
              @click="fetchProjects"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Project Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <svg
                class="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                ></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Projects</p>
              <p class="text-2xl font-semibold text-gray-900">{{ projects.length }}</p>
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
              <p class="text-sm font-medium text-gray-600">My Projects</p>
              <p class="text-2xl font-semibold text-gray-900">{{ myProjectsCount }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 rounded-lg">
              <svg
                class="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Collaborating</p>
              <p class="text-2xl font-semibold text-gray-900">{{ collaboratingCount }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-purple-100 rounded-lg">
              <svg
                class="w-6 h-6 text-purple-600"
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
              <p class="text-2xl font-semibold text-gray-900">{{ totalTasksCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-6 mb-6">
        <div class="flex items-center mb-4">
          <svg
            class="w-6 h-6 text-red-600 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <h3 class="text-lg font-medium text-red-800">Error</h3>
        </div>
        <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
        <div class="mt-4 space-x-2">
          <button
            @click="fetchProjects"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
          >
            Try Again
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Projects Grid -->
      <div v-else-if="filteredProjects.length > 0">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            Projects ({{ filteredProjects.length
            }}{{ filteredProjects.length !== projects.length ? ` of ${projects.length}` : '' }})
          </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ProjectCard
            v-for="project in filteredProjects"
            :key="project.id"
            :project="project"
            @view="viewProjectDetails"
            @edit="editProject"
            @delete="deleteProject"
          />
        </div>
      </div>

      <!-- Empty/Filtered State -->
      <div v-else-if="projects.length > 0" class="text-center py-8 bg-gray-50 rounded-lg">
        <p class="text-sm text-gray-600">No projects match the current filters.</p>
        <button
          @click="clearFilters"
          class="mt-2 text-sm text-indigo-600 hover:text-indigo-500"
        >
          Clear filters
        </button>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
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
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          ></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No projects</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ProjectCard from '@/components/ProjectCard.vue'

const router = useRouter()
const authStore = useAuthStore()

const KONG_API_URL = 'http://localhost:8000'

// Reactive data
const projects = ref([])
const loading = ref(false)
const error = ref(null)
const showCreateForm = ref(false)
const isCreating = ref(false)

const newProject = ref({
  title: '',
  description: '',
  deadline: '',
})

// --- Collaborator Management State (NEW) ---
const selectedCollaboratorId = ref(null)
const localCollaborators = ref([]) // Collaborators currently selected for the new project
const collaboratorDepartmentFilter = ref('')
const collaboratorRoleFilter = ref('')

// Mock User Data (Replace with real API fetch if available)
const allUsers = ref([])

// Filters and sorting
const filters = ref({
  role: '',
})
const sortBy = ref('default')

// --- Computed properties ---
const myProjectsCount = computed(() => {
  return projects.value.filter((p) => p.user_role === 'owner').length
})

const collaboratingCount = computed(() => {
  return projects.value.filter((p) => p.user_role === 'collaborator').length
})

const totalTasksCount = computed(() => {
  return projects.value.reduce((sum, p) => sum + (p.task_count || 0), 0)
})

const collaboratorDepartments = computed(() => [
  ...new Set(allUsers.value.map((u) => u.department).filter(Boolean)),
])

const collaboratorRoles = computed(() => [
  ...new Set(allUsers.value.map((u) => u.role).filter(Boolean)),
])

const availableCollaborators = computed(() => {
  const currentCollaboratorIds = localCollaborators.value.map((c) => c.user_id)
  const currentUserId = authStore.currentUserId

  return allUsers.value
    .filter((user) => user.id !== currentUserId) // Exclude owner
    .filter((user) => !currentCollaboratorIds.includes(user.id)) // Exclude already added
    .filter(
      (user) =>
        !collaboratorDepartmentFilter.value ||
        user.department === collaboratorDepartmentFilter.value,
    )
    .filter((user) => !collaboratorRoleFilter.value || user.role === collaboratorRoleFilter.value)
})

// Filtered and sorted projects
const filteredProjects = computed(() => {
  let filtered = [...projects.value]

  // Filter by role
  if (filters.value.role) {
    filtered = filtered.filter((project) => project.user_role === filters.value.role)
  }

  // Apply sorting
  if (sortBy.value === 'deadline-earliest') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(a.deadline) - new Date(b.deadline)
    })
  } else if (sortBy.value === 'deadline-latest') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1
      if (!b.deadline) return -1
      return new Date(b.deadline) - new Date(a.deadline)
    })
  } else if (sortBy.value === 'title-asc') {
    filtered.sort((a, b) => a.title.localeCompare(b.title))
  } else if (sortBy.value === 'title-desc') {
    filtered.sort((a, b) => b.title.localeCompare(a.title))
  }

  return filtered
})

// Date and Time helpers
const formatDateForInput = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const minDeadline = computed(() => {
  // Always set minimum deadline to the current time for new project creation
  return formatDateForInput(new Date())
})

// --- Collaborator Methods (NEW) ---
const addCollaborator = () => {
  if (!selectedCollaboratorId.value) return

  const userToAdd = allUsers.value.find((u) => u.id === selectedCollaboratorId.value)
  if (userToAdd) {
    // Add the collaborator object to the local list
    localCollaborators.value.push({
      user_id: userToAdd.id,
      name: userToAdd.name,
      role: userToAdd.role,
    })
    selectedCollaboratorId.value = null // Reset selection
  }
}

const removeCollaborator = (userId) => {
  localCollaborators.value = localCollaborators.value.filter((c) => c.user_id !== userId)
}
// --- End Collaborator Methods ---

// API functions
const fetchProjects = async () => {
  try {
    loading.value = true
    error.value = null

    const userId = authStore.currentUserId
    const response = await fetch(`${KONG_API_URL}/projects/user/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`)
    }

    const data = await response.json()
    projects.value = data
  } catch (err) {
    console.error('Error fetching projects:', err)
    error.value = `Failed to fetch projects: ${err.message}`
    projects.value = []
  } finally {
    loading.value = false
  }
}

const createProject = async () => {
  try {
    isCreating.value = true
    error.value = null

    // Get collaborator IDs for the payload
    const collaboratorIds = localCollaborators.value.map((c) => c.user_id)
    console.log(collaboratorIds)
    const projectData = {
      title: newProject.value.title,
      description: newProject.value.description || null,
      deadline: newProject.value.deadline || null,
      owner_id: authStore.currentUserId,
      collaborator_ids: collaboratorIds, // INCLUDED COLLABORATORS
    }

    const response = await fetch(`${KONG_API_URL}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(projectData),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to create project')
    }

    const createdProject = await response.json()

    // Add user_role for display
    createdProject.user_role = 'owner'
    createdProject.task_count = 0

    // Add to projects list
    projects.value.unshift(createdProject)

    // Reset form
    newProject.value = {
      title: '',
      description: '',
      deadline: '',
    }
    localCollaborators.value = [] // Reset collaborators
    selectedCollaboratorId.value = null
    showCreateForm.value = false
  } catch (err) {
    console.error('Error creating project:', err)
    error.value = `Failed to create project: ${err.message}`
  } finally {
    isCreating.value = false
  }
}

const viewProjectDetails = (projectId) => {
  router.push(`/projects/${projectId}`)
}

const fetchAllUsers = async () => {
  try {
    // Assume you have an endpoint that returns all users
    const response = await fetch(`${KONG_API_URL}/user`)
    if (response.ok) {
      allUsers.value = await response.json()
    } else {
      console.error('Failed to fetch all users.')
    }
  } catch (err) {
    console.error('Error fetching all users:', err)
  }
}

// Filter and sort functions
const applyFilters = () => {
  // Filters are applied reactively via computed property
}

const clearFilters = () => {
  filters.value.role = ''
  sortBy.value = 'default'
}

// Edit project function
const editProject = (project) => {
  router.push(`/projects/${project.id}`)
}

// Delete project function
const deleteProject = async (projectId) => {
  if (!confirm('Are you sure you want to delete this project?')) return

  try {
    const response = await fetch(`${KONG_API_URL}/projects/${projectId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: authStore.currentUserId })
    })

    if (response.ok) {
      alert('Project deleted successfully')
      await fetchProjects()
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to delete project')
    }
  } catch (err) {
    console.error('Error deleting project:', err)
    alert('Failed to delete project: ' + err.message)
  }
}

// Lifecycle
onMounted(() => {
  fetchProjects()
  fetchAllUsers()
})
</script>
