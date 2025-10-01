<template>
    <div class="min-h-screen bg-gray-50">
      <!-- Navigation Bar -->
      <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center h-16">
            <!-- Left side - Logo and Navigation Links -->
            <div class="flex items-center space-x-8">
              <div class="flex-shrink-0">
                <h1 class="text-xl font-bold text-gray-900">TaskBoard</h1>
              </div>
              
              <!-- Navigation Links -->
              <div class="hidden md:block">
                <div class="ml-10 flex items-baseline space-x-4">
                  <router-link to="/tasks" 
                             class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                             :class="isActiveRoute('/tasks') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
                    <div class="flex items-center">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                      </svg>
                      Tasks
                    </div>
                  </router-link>
                  
                  <router-link to="/projects" 
                             class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                             :class="isActiveRoute('/projects') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
                    <div class="flex items-center">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                      </svg>
                      Projects
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
  
            <!-- Right side - User info and actions -->
            <div class="flex items-center space-x-4">
              <!-- User Badge -->
              <div class="flex items-center space-x-3">
                <div class="hidden sm:block text-right">
                  <p class="text-sm font-medium text-gray-900">{{ authStore.user?.name || 'User' }}</p>
                  <p class="text-xs text-gray-500 capitalize">{{ authStore.user?.role || 'staff' }}</p>
                </div>
                <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
              </div>
              
              <!-- Logout Button -->
              <button @click="authStore.logout()" 
                      class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                Logout
              </button>
              
              <!-- Mobile menu button -->
              <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
                  <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Mobile Navigation Menu -->
          <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 py-3">
            <div class="space-y-1">
              <router-link to="/tasks" @click="mobileMenuOpen = false"
                         class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
                         :class="isActiveRoute('/tasks') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  Tasks
                </div>
              </router-link>
              
              <router-link to="/projects" @click="mobileMenuOpen = false"
                         class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
                         :class="isActiveRoute('/projects') ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                  </svg>
                  Projects
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </nav>
  
      <!-- Page Content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Page Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Project Taskboard</h1>
          <p class="text-sm text-gray-600 mt-1">Manage projects and collaborate with your team</p>
        </div>
  
        <!-- Create Project Button -->
        <div class="mb-6">
          <button @click="showCreateForm = !showCreateForm" 
                  class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            {{ showCreateForm ? 'Cancel' : 'Create New Project' }}
          </button>
        </div>
  
        <!-- Create Project Form -->
        <div v-if="showCreateForm" class="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Create New Project</h3>
          <form @submit.prevent="createProject" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="title" class="block text-sm font-medium text-gray-700">Project Title</label>
                <input v-model="newProject.title" type="text" id="title" required 
                       class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div>
                <label for="deadline" class="block text-sm font-medium text-gray-700">Deadline</label>
                <input v-model="newProject.deadline" type="datetime-local" id="deadline" 
                       class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
              </div>
            </div>
            <div>
              <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
              <textarea v-model="newProject.description" id="description" rows="3" 
                        class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"></textarea>
            </div>
            <div>
              <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
              <select v-model="newProject.status" id="status" required 
                      class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                <option value="Planning">Planning</option>
                <option value="Active">Active</option>
                <option value="On Hold">On Hold</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
            <div class="flex justify-end space-x-3">
              <button type="button" @click="showCreateForm = false" 
                      class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                Cancel
              </button>
              <button type="submit" :disabled="isCreating" 
                      class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md text-sm font-medium disabled:opacity-50">
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
                <p class="text-sm font-medium text-gray-600">Active Projects</p>
                <p class="text-2xl font-semibold text-gray-900">{{ getProjectCountByStatus('Active') }}</p>
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
                <p class="text-sm font-medium text-gray-600">Planning</p>
                <p class="text-2xl font-semibold text-gray-900">{{ getProjectCountByStatus('Planning') }}</p>
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
                <p class="text-sm font-medium text-gray-600">My Tasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ myTasksCount }}</p>
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
  
        <!-- Projects Grid -->
        <div v-if="loading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
        
        <div v-else-if="projects.length === 0 && !error" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No projects found</h3>
          <p class="mt-1 text-sm text-gray-500">Get started by creating your first project.</p>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="project in projects" :key="project.id" 
               class="bg-white rounded-lg shadow-md hover:shadow-xl transition-all duration-200 border-l-4 cursor-pointer transform hover:-translate-y-1"
               :class="getStatusBorderColor(project.status)"
               @click="viewProjectDetails(project.id)">
            
            <div class="p-6">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors">
                    {{ project.title }}
                  </h3>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="getStatusBadgeColor(project.status)">
                    {{ project.status }}
                  </span>
                </div>
                
                <div class="flex items-center space-x-2 ml-4">
                  <button @click.stop="editProject(project)" 
                          class="text-gray-400 hover:text-indigo-600 transition-colors p-1 rounded hover:bg-gray-100"
                          title="Edit Project">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                  </button>
                  <button @click.stop="deleteProject(project.id)" 
                          class="text-gray-400 hover:text-red-600 transition-colors p-1 rounded hover:bg-red-50"
                          title="Delete Project">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </div>
              
              <p class="text-sm text-gray-600 mt-3 line-clamp-2">
                {{ project.description || 'No description available' }}
              </p>
              
              <div v-if="project.deadline" class="flex items-center mt-4 text-sm">
                <svg class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <span :class="getDeadlineColor(project.deadline)">
                  Due: {{ formatDeadline(project.deadline) }}
                </span>
              </div>
              
              <div class="mt-4 grid grid-cols-2 gap-2 text-xs text-gray-600">
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  {{ getProjectTaskCount(project.id) }} tasks
                </div>
                <div class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  {{ getProjectMembersCount(project.id) }} members
                </div>
              </div>
              
              <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
                <span class="text-xs text-gray-500">
                  Created by {{ getProjectOwnerName(project.owner_id) }}
                </span>
                <div class="flex items-center space-x-1">
                  <div v-if="getProjectProgress(project.id) >= 0" class="w-16 bg-gray-200 rounded-full h-2">
                    <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
                         :style="`width: ${getProjectProgress(project.id)}%`"></div>
                  </div>
                  <span class="text-xs text-gray-500">{{ getProjectProgress(project.id) }}%</span>
                </div>
              </div>
            </div>
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
  const tasks = ref([]) // To store all tasks for progress calculation
  const loading = ref(false)
  const error = ref(null)
  const showCreateForm = ref(false)
  const isCreating = ref(false)
  const mobileMenuOpen = ref(false)
  
  const newProject = ref({
    title: '',
    description: '',
    deadline: '',
    status: 'Planning'
  })
  
  // Computed properties
  const myTasksCount = computed(() => {
    return tasks.value.filter(task => 
      task.owner_id === authStore.currentUserId || 
      task.assigned_to === authStore.currentUserId
    ).length
  })
  
  // Navigation helper function
  const isActiveRoute = (routePath) => {
    return router.currentRoute.value.path === routePath || 
           router.currentRoute.value.path.startsWith(routePath + '/')
  }
  
  // Helper functions
  const getProjectCountByStatus = (status) => {
    return projects.value.filter(project => project.status === status).length
  }
  
  const getStatusBorderColor = (status) => {
    const colors = {
      'Planning': 'border-blue-400',
      'Active': 'border-green-400',
      'On Hold': 'border-yellow-400',
      'Completed': 'border-purple-400'
    }
    return colors[status] || 'border-gray-400'
  }
  
  const getStatusBadgeColor = (status) => {
    const colors = {
      'Planning': 'bg-blue-100 text-blue-800',
      'Active': 'bg-green-100 text-green-800',
      'On Hold': 'bg-yellow-100 text-yellow-800',
      'Completed': 'bg-purple-100 text-purple-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
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
  
  const getProjectTaskCount = (projectId) => {
    // For now, return a placeholder. In a real app, you'd filter tasks by project
    return Math.floor(Math.random() * 10) + 1
  }
  
  const getProjectMembersCount = (projectId) => {
    // For now, return a placeholder. In a real app, you'd count project members
    return Math.floor(Math.random() * 5) + 1
  }
  
  const getProjectOwnerName = (ownerId) => {
    // For now, return a placeholder. In a real app, you'd fetch user data
    return ownerId === authStore.currentUserId ? 'You' : 'Team Member'
  }
  
  const getProjectProgress = (projectId) => {
    // For now, return a placeholder. In a real app, you'd calculate based on completed tasks
    return Math.floor(Math.random() * 100)
  }
  
  // API functions
  const fetchProjects = async () => {
    try {
      loading.value = true
      error.value = null
      
      // For now, we'll create mock projects since there's no project API yet
      // In a real implementation, you'd call: const response = await fetch(`${KONG_API_URL}/projects`)
      
      // Mock data structure similar to tasks
      const mockProjects = [
        {
          id: 1,
          title: 'Website Redesign Project',
          description: 'Complete overhaul of the company website with modern design and improved UX',
          deadline: '2025-12-31T23:59:59',
          status: 'Active',
          owner_id: authStore.currentUserId,
          created_at: '2025-09-01T10:00:00'
        },
        {
          id: 2,
          title: 'Mobile App Development',
          description: 'Develop a mobile application for iOS and Android platforms',
          deadline: '2025-11-15T23:59:59',
          status: 'Planning',
          owner_id: 2,
          created_at: '2025-09-15T14:30:00'
        },
        {
          id: 3,
          title: 'Database Migration',
          description: 'Migrate legacy database to new cloud infrastructure',
          deadline: '2025-10-30T23:59:59',
          status: 'On Hold',
          owner_id: authStore.currentUserId,
          created_at: '2025-08-20T09:15:00'
        }
      ]
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      projects.value = mockProjects
      
    } catch (err) {
      console.error('Error fetching projects:', err)
      error.value = `Failed to fetch projects: ${err.message}`
      projects.value = []
    } finally {
      loading.value = false
    }
  }
  
  const fetchTasks = async () => {
    try {
      const response = await fetch(`${KONG_API_URL}/tasks`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        tasks.value = data
      }
    } catch (err) {
      console.error('Error fetching tasks:', err)
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
        status: newProject.value.status,
        owner_id: authStore.currentUserId
      }
      
      // For now, simulate project creation since there's no project API yet
      // In a real implementation: const response = await fetch(`${KONG_API_URL}/projects`, {...})
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Add the new project to the list with a mock ID
      const newProjectData = {
        ...projectData,
        id: Date.now(), // Simple mock ID
        created_at: new Date().toISOString()
      }
      
      projects.value.unshift(newProjectData)
      
      // Reset form
      newProject.value = {
        title: '',
        description: '',
        deadline: '',
        status: 'Planning'
      }
      showCreateForm.value = false
      
    } catch (err) {
      console.error('Error creating project:', err)
      alert('Failed to create project: ' + err.message)
    } finally {
      isCreating.value = false
    }
  }
  
  const viewProjectDetails = (projectId) => {
    router.push(`/projects/${projectId}`)
  }
  
  const editProject = (project) => {
    console.log('Edit project:', project)
    // TODO: Implement edit functionality
  }
  
  const deleteProject = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project?')) return
    
    try {
      // For now, simulate deletion since there's no project API yet
      // In a real implementation: await fetch(`${KONG_API_URL}/projects/${projectId}`, { method: 'DELETE' })
      
      projects.value = projects.value.filter(p => p.id !== projectId)
    } catch (err) {
      console.error('Error deleting project:', err)
      alert('Failed to delete project: ' + err.message)
    }
  }
  
  onMounted(() => {
    if (authStore.isAuthenticated) {
      fetchProjects()
      fetchTasks() // Fetch tasks to calculate stats
    } else {
      authStore.logout()
    }
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