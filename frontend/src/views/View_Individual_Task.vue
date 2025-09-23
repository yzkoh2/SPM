<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">SPM Project</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-700">Welcome, {{ userEmail }}</span>
            <button @click="logout" class="text-red-600 hover:text-red-900 text-sm font-medium">
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Projects Section (Placeholder) -->
      <div class="mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Projects</h2>
        <div class="bg-white rounded-lg shadow-sm p-6">
          <p class="text-gray-500">Project management section - handled by other team members</p>
        </div>
      </div>

      <!-- Individual Tasks Section -->
      <div>
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Individual Tasks</h2>
        
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <p class="mt-2 text-gray-600">Loading your tasks...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error loading tasks</h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
              </div>
              <div class="mt-4">
                <button @click="loadUserTasks" class="bg-red-100 px-3 py-1 rounded text-red-800 text-sm hover:bg-red-200">
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks List -->
        <div v-else class="space-y-4">
          <!-- No Tasks State -->
          <div v-if="tasks.length === 0" class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">No tasks assigned</h3>
            <p class="mt-2 text-gray-500">You don't have any tasks assigned to you at the moment.</p>
          </div>

          <!-- Task Cards -->
          <div v-else class="grid grid-cols-1 gap-4">
            <div
              v-for="task in tasks"
              :key="task.id"
              class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div class="flex justify-between items-start mb-4">
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-900 break-words">{{ task.title }}</h3>
                  <p v-if="task.description" class="mt-1 text-gray-600 line-clamp-2">{{ task.description }}</p>
                </div>
                <span class="ml-4 inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium whitespace-nowrap"
                      :class="getStatusColor(task.status)">
                  {{ task.status }}
                </span>
              </div>

              <!-- Task Metadata -->
              <div class="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-4">
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  <span>{{ formatDeadline(task.deadline) }}</span>
                </div>
                
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  <span>{{ task.subtask_count }} subtasks</span>
                </div>

                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.418 8-8 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.418-8 8-8s8 3.582 8 8z"></path>
                  </svg>
                  <span>{{ task.comment_count }} comments</span>
                </div>

                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path>
                  </svg>
                  <span>{{ task.attachment_count }} files</span>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex justify-between items-center">
                <div class="flex space-x-3">
                  <router-link
                    :to="`/tasks/${task.id}`"
                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                  >
                    View Details
                  </router-link>
                  
                  <button
                    @click="viewSubtasks(task.id)"
                    class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                  >
                    View Subtasks ({{ task.subtask_count }})
                  </button>
                </div>

                <!-- Task ID for reference -->
                <span class="text-xs text-gray-400">Task #{{ task.id }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const tasks = ref([]);
const loading = ref(true);
const error = ref(null);
const userEmail = ref('');
const userId = ref(null);

const KONG_API_URL = "http://localhost:8000";

onMounted(async () => {
  await getCurrentUser();
  if (userId.value) {
    await loadUserTasks();
  }
});

const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    const response = await fetch(`${KONG_API_URL}/user/verifyJWT`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      throw new Error('Failed to verify user');
    }

    const userData = await response.json();
    userEmail.value = userData.email;
    
    // Extract user ID from JWT payload
    const payload = JSON.parse(atob(token.split('.')[1]));
    userId.value = parseInt(payload.sub);
    
  } catch (err) {
    console.error('Error getting current user:', err);
    localStorage.removeItem('authToken');
    router.push('/login');
  }
};

const loadUserTasks = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    console.log('Loading tasks for user:', userId.value);

    const response = await fetch(`${KONG_API_URL}/tasks?owner_id=${userId.value}`, {
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
      throw new Error(`Failed to fetch tasks: ${response.status}`);
    }

    tasks.value = await response.json();
    console.log('Tasks loaded:', tasks.value);
    
  } catch (err) {
    console.error('Error loading tasks:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const logout = () => {
  localStorage.removeItem('authToken');
  router.push('/login');
};

const viewSubtasks = (taskId) => {
  // This will be handled by your teammate's subtask component
  // For now, we'll just navigate to a placeholder route
  console.log('View subtasks for task:', taskId);
  // router.push(`/tasks/${taskId}/subtasks`);
  alert(`View subtasks for task ${taskId} - This will be implemented by your teammate`);
};

// Utility functions
const getStatusColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-blue-100 text-blue-800',
    'In Progress': 'bg-blue-100 text-blue-800', 
    'Completed': 'bg-green-100 text-green-800',
    'Done': 'bg-green-100 text-green-800',
    'On Hold': 'bg-yellow-100 text-yellow-800',
    'Blocked': 'bg-red-100 text-red-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline';
  
  const date = new Date(deadline);
  const now = new Date();
  const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24));
  
  const options = { month: 'short', day: 'numeric' };
  const formatted = date.toLocaleDateString('en-US', options);
  
  if (diffDays < 0) return `${formatted} (Overdue)`;
  if (diffDays === 0) return `${formatted} (Today)`;
  if (diffDays === 1) return `${formatted} (Tomorrow)`;
  if (diffDays <= 7) return `${formatted} (${diffDays} days)`;
  
  return formatted;
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>