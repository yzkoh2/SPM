<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/tasks" class="text-sm text-gray-600 hover:text-gray-900">← Back to Tasks</router-link>
            <div v-if="parentTask">
              <h1 class="text-xl font-semibold text-gray-900">Subtasks</h1>
              <p class="text-sm text-gray-600">for "{{ parentTask.title }}"</p>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center space-x-4">
            <button
              @click="fetchSubtasks"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Task Overview Card -->
        <div v-if="parentTask" class="bg-white overflow-hidden shadow rounded-lg mb-6">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-lg font-medium text-gray-900">{{ parentTask.title }}</h2>
                <p v-if="parentTask.description" class="mt-1 text-sm text-gray-600">{{ parentTask.description }}</p>
              </div>
              <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusColor(parentTask.status)">
                  {{ parentTask.status }}
                </span>
                <router-link 
                  :to="`/tasks/${parentTask.id}`"
                  class="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                >
                  View Full Task →
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p class="mt-2 text-gray-600">Loading subtasks...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error loading subtasks</h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Subtasks List -->
        <div v-else-if="subtasks.length > 0" class="space-y-3">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">Subtasks ({{ subtasks.length }})</h3>
            <div class="flex space-x-2">
              <span class="text-sm text-gray-500">
                {{ completedCount }}/{{ subtasks.length }} completed
              </span>
              <div class="w-24 bg-gray-200 rounded-full h-2 mt-1">
                <div class="bg-green-600 h-2 rounded-full" :style="{ width: progressPercentage + '%' }"></div>
              </div>
            </div>
          </div>

          <div v-for="subtask in subtasks" :key="subtask.id" class="bg-white border rounded-lg p-4 hover:shadow-sm transition-shadow">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3 flex-1">
                
                <!-- Subtask content -->
                <div class="flex-1">
                  <h4 class="text-sm font-medium text-gray-900"
                      :class="{ 'line-through text-gray-500': subtask.status === 'Completed' }">
                    {{ subtask.title }}
                  </h4>
                  <p class="text-xs text-gray-500 mt-1">ID: {{ subtask.id }}</p>
                </div>
              </div>
              
              <!-- Status and Actions -->
              <div class="flex items-center space-x-3">
                <!-- Status Badge -->
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusColor(subtask.status)">
                  {{ subtask.status }}
                </span>
                
                <!-- Status Dropdown -->
                <select 
                  :value="subtask.status"
                  @change="updateSubtaskStatus(subtask, $event.target.value)"
                  class="text-xs border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="Unassigned">Unassigned</option>
                  <option value="Ongoing">Ongoing</option>
                  <option value="Completed">Completed</option>
                  <option value="On Hold">On Hold</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No subtasks found</h3>
          <p class="mt-1 text-sm text-gray-500">This task doesn't have any subtasks yet.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const subtasks = ref([]);
const parentTask = ref(null);
const loading = ref(true);
const error = ref(null);

const KONG_API_URL = "http://localhost:8000";

// Computed properties for progress tracking
const completedCount = computed(() => {
  return subtasks.value.filter(subtask => subtask.status === 'Completed').length;
});

const progressPercentage = computed(() => {
  if (subtasks.value.length === 0) return 0;
  return Math.round((completedCount.value / subtasks.value.length) * 100);
});

// Function to fetch parent task details
async function fetchParentTask() {
  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch task: ${response.status}`);
    }

    parentTask.value = await response.json();
  } catch (err) {
    console.error('Error fetching parent task:', err);
  }
}

// Function to fetch subtasks
async function fetchSubtasks() {
  loading.value = true;
  error.value = null;
  
  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('authToken');
        router.push('/login');
        return;
      }
      if (response.status === 404) {
        throw new Error('Task not found');
      }
      throw new Error(`Failed to fetch subtasks: ${response.status}`);
    }

    subtasks.value = await response.json();
  } catch (err) {
    console.error('Error fetching subtasks:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

// Function to update subtask status
async function updateSubtaskStatus(subtask, newStatus) {
  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks/${subtask.id}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: newStatus
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to update subtask: ${response.status}`);
    }

    // Update local state
    const index = subtasks.value.findIndex(s => s.id === subtask.id);
    if (index !== -1) {
      subtasks.value[index].status = newStatus;
    }

    console.log(`Subtask ${subtask.id} status updated to: ${newStatus}`);
  } catch (err) {
    console.error('Error updating subtask status:', err);
    alert('Failed to update subtask status. Please try again.');
  }
}

// Function to toggle subtask between completed and ongoing
function toggleSubtaskStatus(subtask) {
  const newStatus = subtask.status === 'Completed' ? 'Ongoing' : 'Completed';
  updateSubtaskStatus(subtask, newStatus);
}

// Function to get status color
function getStatusColor(status) {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-blue-100 text-blue-800',
    'Completed': 'bg-green-100 text-green-800',
    'On Hold': 'bg-yellow-100 text-yellow-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}

// Initialize component
onMounted(() => {
  fetchParentTask();
  fetchSubtasks();
});
</script>

<style scoped>
.line-through {
  text-decoration: line-through;
}
</style>