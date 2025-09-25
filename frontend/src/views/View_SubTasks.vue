<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link to="/tasks" class="text-sm text-gray-600 hover:text-gray-900">← Back to Tasks</router-link>
            <router-link 
              :to="`/tasks/${route.params.id}`"
              class="text-sm text-indigo-600 hover:text-indigo-500">
              ← Task Details
            </router-link>
            <div v-if="parentTask">
              <h1 class="text-xl font-semibold text-gray-900">Subtasks</h1>
              <p class="text-sm text-gray-600">for "{{ parentTask.title }}"</p>
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center space-x-4">
            <button
              @click="showCreateDialog = true"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Add Subtask
            </button>
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
              <div class="flex-1">
                <h2 class="text-lg font-medium text-gray-900">{{ parentTask.title }}</h2>
                <p v-if="parentTask.description" class="mt-1 text-sm text-gray-600 line-clamp-2">
                  {{ parentTask.description }}
                </p>
                
                <!-- Task metadata -->
                <div class="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                  <span class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                    Owner: User {{ parentTask.owner_id }}
                  </span>
                  <span v-if="parentTask.assigned_to" class="flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                    Assigned: User {{ parentTask.assigned_to }}
                  </span>
                  <span v-else class="flex items-center text-orange-600">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Unassigned
                  </span>
                </div>
              </div>
              
              <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusColor(parentTask.status)">
                  {{ formatStatus(parentTask.status) }}
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

        <!-- Progress Summary -->
        <div v-if="subtasks.length > 0" class="bg-white rounded-lg shadow-md p-6 mb-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">Progress Overview</h3>
            <div class="text-sm text-gray-500">
              {{ completedCount }}/{{ subtasks.length }} completed ({{ progressPercentage }}%)
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div class="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div class="bg-green-600 h-3 rounded-full transition-all duration-500" 
                 :style="{ width: progressPercentage + '%' }"></div>
          </div>
          
          <!-- Status Breakdown -->
          <div class="flex flex-wrap gap-2">
            <span 
              v-for="(count, status) in statusSummary" 
              :key="status"
              v-if="count > 0"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
              :class="getStatusColor(status)"
            >
              {{ count }} {{ formatStatus(status) }}
            </span>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
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
              <div class="mt-4">
                <button @click="fetchSubtasks" 
                        class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm">
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Subtasks List -->
        <div v-else-if="subtasks.length > 0" class="space-y-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">Subtasks ({{ subtasks.length }})</h3>
            
            <!-- Filter Options -->
            <div class="flex items-center space-x-3">
              <select v-model="statusFilter" @change="applyFilters"
                      class="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
                <option value="">All Statuses</option>
                <option value="unassigned">Unassigned</option>
                <option value="ongoing">Ongoing</option>
                <option value="under_review">Under Review</option>
                <option value="completed">Completed</option>
              </select>
              
              <select v-model="assigneeFilter" @change="applyFilters"
                      class="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500">
                <option value="">All Assignees</option>
                <option value="unassigned">Unassigned</option>
                <option v-for="assignee in uniqueAssignees" :key="assignee" :value="assignee">
                  User {{ assignee }}
                </option>
              </select>
            </div>
          </div>

          <div v-for="subtask in filteredSubtasks" :key="subtask.id" 
               class="bg-white border rounded-lg p-4 hover:shadow-sm transition-shadow">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3 flex-1">
                <!-- Status indicator -->
                <div class="w-3 h-3 rounded-full" :class="getStatusIndicatorColor(subtask.status)"></div>
                
                <!-- Subtask content -->
                <div class="flex-1">
                  <h4 class="text-sm font-medium text-gray-900"
                      :class="{ 'line-through text-gray-500': subtask.status === 'completed' }">
                    {{ subtask.title }}
                  </h4>
                  <p v-if="subtask.description" class="text-sm text-gray-600 mt-1 line-clamp-2">
                    {{ subtask.description }}
                  </p>
                  
                  <!-- Subtask metadata -->
                  <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>ID: {{ subtask.id }}</span>
                    <span v-if="subtask.assigned_to">Assigned to User {{ subtask.assigned_to }}</span>
                    <span v-else class="text-orange-600">Unassigned</span>
                    <span>{{ formatDate(subtask.created_at) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Actions -->
              <div class="flex items-center space-x-3 ml-4">
                <!-- Status Badge -->
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusColor(subtask.status)">
                  {{ formatStatus(subtask.status) }}
                </span>
                
                <!-- Quick Actions -->
                <div class="flex items-center space-x-1">
                  <!-- Assign Button -->
                  <button @click="showAssignDialog(subtask)"
                          class="p-1 text-gray-400 hover:text-indigo-600 transition-colors"
                          title="Assign Subtask">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                  </button>
                  
                  <!-- Complete Toggle -->
                  <button @click="toggleSubtaskCompletion(subtask)"
                          class="p-1 transition-colors"
                          :class="subtask.status === 'completed' ? 'text-green-600 hover:text-green-700' : 'text-gray-400 hover:text-green-600'"
                          :title="subtask.status === 'completed' ? 'Mark Incomplete' : 'Mark Complete'">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </button>
                </div>
                
                <!-- Status Dropdown -->
                <select 
                  :value="subtask.status"
                  @change="updateSubtaskStatus(subtask, $event.target.value)"
                  class="text-xs border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="unassigned">Unassigned</option>
                  <option value="ongoing">Ongoing</option>
                  <option value="under_review">Under Review</option>
                  <option value="completed">Completed</option>
                </select>

                <!-- View Details Button -->
                <router-link 
                  :to="`/tasks/${route.params.id}/subtasks/${subtask.id}`"
                  class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  Details
                </router-link>
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
          <p class="mt-1 text-sm text-gray-500">Get started by creating your first subtask.</p>
          <div class="mt-6">
            <button @click="showCreateDialog = true"
                    class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
              Add Subtask
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Subtask Dialog -->
    <div v-if="showCreateDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Create New Subtask</h3>
        
        <form @submit.prevent="createSubtask" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Title</label>
            <input 
              v-model="newSubtask.title" 
              type="text" 
              required
              placeholder="Enter subtask title"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea 
              v-model="newSubtask.description" 
              rows="3"
              placeholder="Enter subtask description (optional)"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select 
                v-model="newSubtask.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="unassigned">Unassigned</option>
                <option value="ongoing">Ongoing</option>
                <option value="under_review">Under Review</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Assign to (Optional)</label>
              <input 
                v-model="newSubtask.assigned_to" 
                type="number" 
                placeholder="User ID"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
          </div>
          
          <div class="flex justify-end space-x-3">
            <button type="button" @click="cancelCreateSubtask" 
                    class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
              Cancel
            </button>
            <button type="submit" :disabled="!newSubtask.title || isCreating"
                    class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
              {{ isCreating ? 'Creating...' : 'Create Subtask' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assign Subtask Dialog -->
    <div v-if="showAssignSubtaskDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">
          {{ selectedSubtask?.assigned_to ? 'Reassign Subtask' : 'Assign Subtask' }}
        </h3>
        <p class="text-sm text-gray-600 mb-4">Subtask: "{{ selectedSubtask?.title }}"</p>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Assign to User ID:
          </label>
          <input 
            v-model="assignmentUserId" 
            type="number" 
            placeholder="Enter user ID"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button @click="cancelAssignSubtask" 
                  class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
            Cancel
          </button>
          <button @click="assignSubtask" :disabled="!assignmentUserId"
                  class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md disabled:opacity-50">
            Assign
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

// Reactive data
const subtasks = ref([]);
const parentTask = ref(null);
const loading = ref(true);
const error = ref(null);
const showCreateDialog = ref(false);
const showAssignSubtaskDialog = ref(false);
const isCreating = ref(false);

// Filters
const statusFilter = ref('');
const assigneeFilter = ref('');

// Assignment dialog
const selectedSubtask = ref(null);
const assignmentUserId = ref('');

// New subtask form
const newSubtask = ref({
  title: '',
  description: '',
  status: 'unassigned',
  assigned_to: null
});

// API configuration
const KONG_API_URL = "http://localhost:8000";
const currentUserId = 1;

// Computed properties
const completedCount = computed(() => {
  return subtasks.value.filter(subtask => subtask.status === 'completed').length;
});

const progressPercentage = computed(() => {
  if (subtasks.value.length === 0) return 0;
  return Math.round((completedCount.value / subtasks.value.length) * 100);
});

const statusSummary = computed(() => {
  const summary = {};
  subtasks.value.forEach(subtask => {
    summary[subtask.status] = (summary[subtask.status] || 0) + 1;
  });
  return summary;
});

const uniqueAssignees = computed(() => {
  const assignees = new Set();
  subtasks.value.forEach(subtask => {
    if (subtask.assigned_to) {
      assignees.add(subtask.assigned_to);
    }
  });
  return Array.from(assignees).sort((a, b) => a - b);
});

const filteredSubtasks = computed(() => {
  let filtered = [...subtasks.value];
  
  if (statusFilter.value) {
    filtered = filtered.filter(subtask => subtask.status === statusFilter.value);
  }
  
  if (assigneeFilter.value) {
    if (assigneeFilter.value === 'unassigned') {
      filtered = filtered.filter(subtask => !subtask.assigned_to);
    } else {
      filtered = filtered.filter(subtask => subtask.assigned_to == assigneeFilter.value);
    }
  }
  
  return filtered;
});

// Methods
const fetchParentTask = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      parentTask.value = await response.json();
    } else {
      console.warn('Failed to fetch parent task details');
    }
  } catch (err) {
    console.error('Error fetching parent task:', err);
  }
};

const fetchSubtasks = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks`, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      subtasks.value = await response.json();
    } else if (response.status === 404) {
      error.value = 'Task not found';
    } else {
      error.value = `Failed to fetch subtasks: ${response.status}`;
    }
  } catch (err) {
    console.error('Error fetching subtasks:', err);
    error.value = `Failed to connect to server: ${err.message}`;
  } finally {
    loading.value = false;
  }
};

const createSubtask = async () => {
  if (!newSubtask.value.title) return;
  
  try {
    isCreating.value = true;
    
    const subtaskData = {
      title: newSubtask.value.title,
      description: newSubtask.value.description || null,
      status: newSubtask.value.status,
      created_by: currentUserId,
      assigned_to: newSubtask.value.assigned_to || null
    };
    
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}/subtasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(subtaskData)
    });
    
    if (response.ok) {
      await fetchSubtasks(); // Refresh list
      cancelCreateSubtask();
      alert('Subtask created successfully!');
    } else {
      const errorText = await response.text();
      throw new Error(`Failed to create subtask: ${response.status} - ${errorText}`);
    }
  } catch (err) {
    console.error('Error creating subtask:', err);
    alert('Failed to create subtask: ' + err.message);
  } finally {
    isCreating.value = false;
  }
};

const cancelCreateSubtask = () => {
  showCreateDialog.value = false;
  newSubtask.value = {
    title: '',
    description: '',
    status: 'unassigned',
    assigned_to: null
  };
};

const updateSubtaskStatus = async (subtask, newStatus) => {
  try {
    const response = await fetch(`${KONG_API_URL}/subtasks/${subtask.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: newStatus,
        updated_by: currentUserId
      })
    });

    if (response.ok) {
      // Update local state
      const index = subtasks.value.findIndex(s => s.id === subtask.id);
      if (index !== -1) {
        subtasks.value[index].status = newStatus;
      }
    } else {
      throw new Error(`Failed to update subtask: ${response.status}`);
    }
  } catch (err) {
    console.error('Error updating subtask status:', err);
    alert('Failed to update subtask status. Please try again.');
  }
};

const toggleSubtaskCompletion = async (subtask) => {
  const newStatus = subtask.status === 'completed' ? 'ongoing' : 'completed';
  await updateSubtaskStatus(subtask, newStatus);
};

const showAssignDialog = (subtask) => {
  selectedSubtask.value = subtask;
  assignmentUserId.value = subtask.assigned_to || '';
  showAssignSubtaskDialog.value = true;
};

const assignSubtask = async () => {
  if (!assignmentUserId.value || !selectedSubtask.value) return;
  
  try {
    const response = await fetch(`${KONG_API_URL}/subtasks/${selectedSubtask.value.id}/assign`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        assigned_to: parseInt(assignmentUserId.value),
        updated_by: currentUserId
      })
    });

    if (response.ok) {
      await fetchSubtasks(); // Refresh list
      cancelAssignSubtask();
      alert('Subtask assigned successfully!');
    } else {
      throw new Error(`Failed to assign subtask: ${response.status}`);
    }
  } catch (err) {
    console.error('Error assigning subtask:', err);
    alert('Failed to assign subtask: ' + err.message);
  }
};

const cancelAssignSubtask = () => {
  showAssignSubtaskDialog.value = false;
  selectedSubtask.value = null;
  assignmentUserId.value = '';
};

const applyFilters = () => {
  // Filters are applied automatically via computed property
};

// Utility functions
const getStatusColor = (status) => {
  const colors = {
    'unassigned': 'bg-gray-100 text-gray-800',
    'ongoing': 'bg-yellow-100 text-yellow-800',
    'under_review': 'bg-orange-100 text-orange-800',
    'completed': 'bg-green-100 text-green-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

const getStatusIndicatorColor = (status) => {
  const colors = {
    'unassigned': 'bg-gray-400',
    'ongoing': 'bg-yellow-400',
    'under_review': 'bg-orange-400',
    'completed': 'bg-green-400'
  };
  return colors[status] || 'bg-gray-400';
};

const formatStatus = (status) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatDate = (dateString) => {
  if (!dateString) return 'Not specified';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
};

// Initialize component
onMounted(() => {
  fetchParentTask();
  fetchSubtasks();
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-through {
  text-decoration: line-through;
}
</style>