<template>
  <div class="p-6 max-w-5xl mx-auto">
    <!-- Navigation -->
    <div class="mb-6">
      <router-link to="/tasks" class="text-sm text-gray-600 hover:text-gray-900">← Back to Tasks</router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-gray-600">Loading task details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error loading task</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Details -->
    <div v-else class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start mb-4">
          <h1 class="text-2xl font-bold text-gray-900">{{ task.title }}</h1>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusColor(task.status)">
            {{ task.status }}
          </span>
        </div>
        
        <p v-if="task.description" class="text-gray-600 mb-4">{{ task.description }}</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p><span class="font-semibold">Deadline:</span> {{ formatDate(task.deadline) || 'N/A' }}</p>
            <p><span class="font-semibold">Owner ID:</span> {{ task.owner_id }}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-6 flex space-x-3">
          <router-link 
            :to="`/tasks/${task.id}/subtasks`"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            View Subtasks ({{ task.subtasks?.length || 0 }})
          </router-link>
        </div>
      </div>

      <!-- Subtasks -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Subtasks ({{ task.subtasks?.length || 0 }})</h2>
        <ul v-if="task.subtasks?.length > 0">
          <li
            v-for="sub in task.subtasks"
            :key="sub.id"
            class="border-b py-3 flex justify-between items-center last:border-b-0"
          >
            <span class="text-gray-900">{{ sub.title }}</span>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusColor(sub.status)">
              {{ sub.status }}
            </span>
          </li>
        </ul>
        <p v-else class="text-gray-500">No subtasks yet.</p>
      </div>

      <!-- Comments -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Comments ({{ task.comments?.length || 0 }})</h2>
        <ul v-if="task.comments?.length > 0">
          <li
            v-for="comment in task.comments"
            :key="comment.id"
            class="border-b py-3 last:border-b-0"
          >
            <p class="text-gray-800">{{ comment.body }}</p>
            <p class="text-sm text-gray-500 mt-1">Author ID: {{ comment.author_id }}</p>
          </li>
        </ul>
        <p v-else class="text-gray-500">No comments yet.</p>
      </div>

      <!-- Attachments -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Attachments ({{ task.attachments?.length || 0 }})</h2>
        <ul v-if="task.attachments?.length > 0">
          <li
            v-for="att in task.attachments"
            :key="att.id"
            class="py-2"
          >
            <a :href="att.url" target="_blank" class="text-indigo-600 hover:underline">
              {{ att.filename }}
            </a>
          </li>
        </ul>
        <p v-else class="text-gray-500">No attachments.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const task = ref({
  title: '',
  description: '',
  deadline: null,
  status: '',
  owner_id: null,
  subtasks: [],
  comments: [],
  attachments: []
});
const loading = ref(true);
const error = ref(null);

// CRITICAL FIX: Use Kong URL, not direct service URL
const KONG_API_URL = "http://localhost:8000"; // Changed from 6001 to 8000

onMounted(async () => {
  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    console.log('Making request to:', `${KONG_API_URL}/tasks/${route.params.id}`);

    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
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
      throw new Error(`Failed to fetch task details: ${response.status}`);
    }

    task.value = await response.json();
    console.log('Task loaded:', task.value);
  } catch (err) {
    console.error('Error loading task details:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
});

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

// Function to format date
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
}
</script>