<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header with Create Button -->
      <div class="flex justify-between items-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900">My Projects</h2>
        <button @click="showCreateForm = !showCreateForm" 
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Project
        </button>
      </div>

      <!-- Create Project Form -->
      <div v-if="showCreateForm" class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Create New Project</h3>
        <form @submit.prevent="createProject">
          <div class="grid grid-cols-1 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input v-model="newProject.title" type="text" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                     placeholder="Enter project title">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea v-model="newProject.description" rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        placeholder="Enter project description"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline *</label>
              <input v-model="newProject.deadline" type="datetime-local" required
                     class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
            </div>
          </div>
          <div class="mt-4 flex justify-end space-x-3">
            <button type="button" @click="showCreateForm = false"
                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" :disabled="isCreating"
                    class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400">
              {{ isCreating ? 'Creating...' : 'Create Project' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Project Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
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
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
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
          <svg class="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3 class="text-lg font-medium text-red-800">Error</h3>
        </div>
        <pre class="text-red-700 text-sm whitespace-pre-wrap">{{ error }}</pre>
        <div class="mt-4 space-x-2">
          <button @click="fetchProjects" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md">
            Try Again
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Projects Grid -->
      <div v-else-if="projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="project in projects" :key="project.id" 
             class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden cursor-pointer"
             @click="viewProjectDetails(project.id)">
          <div class="p-6">
            <div class="flex justify-between items-start mb-3">
              <h3 class="text-lg font-semibold text-gray-900 line-clamp-1">{{ project.title }}</h3>
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', getUserRoleBadgeColor(project.user_role)]">
                {{ project.user_role === 'owner' ? 'Owner' : 'Collaborator' }}
              </span>
            </div>
            
            <p class="text-sm text-gray-600 mb-4 line-clamp-2">{{ project.description || 'No description' }}</p>
            
            <div class="space-y-2 text-xs text-gray-600">
              <div class="flex items-center" :class="getDeadlineColor(project.deadline)">
                <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                {{ formatDeadline(project.deadline) }}
              </div>
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  {{ project.task_count || 0 }} tasks
                </div>
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  {{ (project.collaborator_ids?.length || 0) + 1 }} members
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No projects</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
        <div class="mt-6">
          <button @click="showCreateForm = true"
                  class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            New Project
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const KONG_API_URL = "http://localhost:8000"

// Reactive data
const projects = ref([])
const loading = ref(false)
const error = ref(null)
const showCreateForm = ref(false)
const isCreating = ref(false)

const newProject = ref({
  title: '',
  description: '',
  deadline: ''
})

// Computed properties
const myProjectsCount = computed(() => {
  return projects.value.filter(p => p.user_role === 'owner').length
})

const collaboratingCount = computed(() => {
  return projects.value.filter(p => p.user_role === 'collaborator').length
})

const totalTasksCount = computed(() => {
  return projects.value.reduce((sum, p) => sum + (p.task_count || 0), 0)
})

// Helper functions
const getUserRoleBadgeColor = (role) => {
  return role === 'owner' 
    ? 'bg-indigo-100 text-indigo-800' 
    : 'bg-green-100 text-green-800'
}

const getDeadlineColor = (deadline) => {
  if (!deadline) return 'text-gray-600'
  
  const now = new Date()
  const deadlineDate = new Date(deadline)
  
  if (deadlineDate < now) return 'text-red-600 font-medium'
  if (deadlineDate.toDateString() === now.toDateString()) return 'text-orange-600 font-medium'
  return 'text-gray-900'
}

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline set'
  const date = new Date(deadline)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// API functions
const fetchProjects = async () => {
  try {
    loading.value = true
    error.value = null
    
    const userId = authStore.currentUserId
    const response = await fetch(`${KONG_API_URL}/projects/user/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
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
    
    const projectData = {
      title: newProject.value.title,
      description: newProject.value.description || null,
      deadline: newProject.value.deadline || null,
      owner_id: authStore.currentUserId
    }
    
    const response = await fetch(`${KONG_API_URL}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(projectData)
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
      deadline: ''
    }
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

// Lifecycle
onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>