<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900">Dashboard</h1>
          </div>
          
          <!-- User Info and Logout -->
          <div class="flex items-center space-x-4">
            <div v-if="currentUser" class="text-sm text-gray-700">
              Welcome, {{ currentUser.email }}
            </div>
            
            <button
              @click="handleLogout"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
            >
              <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Loading State -->
        <div v-if="loading" class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p class="mt-2 text-gray-600">Loading user information...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error loading user information</h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- User Information Display -->
        <div v-else-if="currentUser" class="space-y-6">
          <!-- User Profile Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <h2 class="text-lg font-medium text-gray-900 mb-4">User Information</h2>
              <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt class="text-sm font-medium text-gray-500">User ID</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ currentUser.id }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Email</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ currentUser.email }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Username</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ currentUser.username }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Role</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getRoleColor(currentUser.role)">
                      {{ currentUser.role }}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUser = ref(null);
const loading = ref(true);
const error = ref(null);

// Use the same API URL as your login
const KONG_API_URL = "http://localhost:8000";

// Function to decode JWT token (client-side)
function decodeJWT(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }

    const payload = parts[1];
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    const decodedPayload = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
    
    return JSON.parse(decodedPayload);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
}

// Function to get user details from backend using user ID
async function getUserDetails() {
  const token = localStorage.getItem('authToken');
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  try {
    const payload = decodeJWT(token);
    if (!payload || !payload.sub) {
      throw new Error('Invalid token payload');
    }

    const userId = payload.sub;
    
    const response = await fetch(`${KONG_API_URL}/user/${userId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Your session has expired. Please login again.');
      }
      throw new Error(`Failed to fetch user: ${response.status}`);
    }

    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Error getting user details:', error);
    throw error;
  }
}

// Function to fetch user data
async function fetchUserData() {
  loading.value = true;
  error.value = null;
  
  try {
    currentUser.value = await getUserDetails();
    console.log('Current user loaded:', currentUser.value);
  } catch (err) {
    console.error('Failed to load user data:', err);
    error.value = err.message;
    
    if (err.message.includes('session has expired') || err.message.includes('authentication token')) {
      localStorage.removeItem('authToken');
      router.push('/login');
    }
  } finally {
    loading.value = false;
  }
}

// Logout function
function handleLogout() {
  localStorage.removeItem('authToken');
  localStorage.removeItem('userPreferences');
  sessionStorage.clear();
  
  currentUser.value = null;
  console.log('Logout successful');
  router.push('/login');
}

// Navigation functions
function navigateToTask(taskId) {
  router.push(`/tasks/${taskId}`);
}

function navigateToSubtasks(taskId) {
  router.push(`/tasks/${taskId}/subtasks`);
}

// Function to get role-specific styling
function getRoleColor(role) {
  const colors = {
    'staff': 'bg-blue-100 text-blue-800',
    'manager': 'bg-green-100 text-green-800',
    'director': 'bg-purple-100 text-purple-800',
    'admin': 'bg-red-100 text-red-800'
  };
  return colors[role] || 'bg-gray-100 text-gray-800';
}

// Load user data when component mounts
onMounted(() => {
  fetchUserData();
});
</script>