<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-8">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">{{ formTitle }}</h2>
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ isSubtask ? 'Subtask Title' : 'Task Title' }}
        </label>
        <input v-model="localData.title" type="text" required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
        <input v-model="localData.deadline" type="datetime-local" :min="minDeadline"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea v-model="localData.description" rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="Describe the task in detail..."></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
        <select v-model="localData.status"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
          <option value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Priority</label>
        <input v-model="localData.priority" type="range" min="1" max="10"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer">
        <div class="flex justify-between text-xs text-gray-600 mt-1">
          <span v-for="n in 10" :key="n">{{ n }}</span>
        </div>
      </div>

      <div>
        <label class="flex items-center">
          <input v-model="localData.is_recurring" type="checkbox"
            class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50">
          <span class="ml-2 text-sm text-gray-600">Is this a recurring task?</span>
        </label>
      </div>

      <div v-if="localData.is_recurring">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence Interval</label>
          <select v-model="localData.recurrence_interval"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div v-if="localData.recurrence_interval === 'custom'">
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence Days</label>
          <input v-model="localData.recurrence_days" type="number"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence End Date</label>
          <input v-model="localData.recurrence_end_date" type="datetime-local" :min="minRecurrenceEndDate"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
        </div>
      </div>

      <div v-if="isEditMode && hierarchicalUsers.length > 0" class="border-t pt-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Assign New Owner</label>
        
        <div class="grid grid-cols-2 gap-4 mb-3">
          <div>
            <label class="block text-xs text-gray-500">Filter by Department</label>
            <select v-model="departmentFilter" class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept" :value="dept">
                {{ dept }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-500">Filter by Team</label>
            <select v-model="teamFilter" class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border">
              <option value="">All Teams</option>
              <option v-for="team in teams" :key="team" :value="team">
                {{ team }}
              </option>
            </select>
          </div>
        </div>

        <select 
          v-model="localData.owner_id"
          class="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
        >
          <option :value="taskToEdit.owner_id" disabled>-- Select a user to transfer to --</option>
          <option v-for="user in filteredUsers" :key="user.id" :value="user.id">
            {{ user.name }} ({{ user.role }})
          </option>
        </select>
      </div>

       <div v-else-if="isEditMode" class="border-t pt-6">
         <label class="block text-sm font-medium text-gray-700">Owner</label>
         <p class="text-xs text-gray-500 mt-1">Your role does not permit transferring this task.</p>
      </div>


      <div class="flex justify-end space-x-3 pt-4">
        <button type="button" @click="$emit('cancel')"
          class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors">
          Cancel
        </button>
        <button type="submit" :disabled="isSubmitting"
          class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors disabled:opacity-50">
          {{ isSubmitting ? submitButtonLoadingText : submitButtonText }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const props = defineProps({
  isSubtask: { type: Boolean, default: false },
  isSubmitting: { type: Boolean, default: false },
  submitButtonText: { type: String, default: 'Create Task' },
  submitButtonLoadingText: { type: String, default: 'Creating...' },
  taskToEdit: { type: Object, default: null },
  allUsers: { type: Array, default: () => [] }
})

const emit = defineEmits(['submit', 'cancel'])

const isEditMode = computed(() => !!props.taskToEdit)
const formTitle = computed(() => isEditMode.value ? (props.isSubtask ? 'Edit Subtask' : 'Edit Task') : (props.isSubtask ? 'Create New Subtask' : 'Create New Task'))

const defaultFormData = {
  title: '',
  deadline: '',
  description: '',
  status: 'Unassigned',
  priority: 5,
  is_recurring: false,
  recurrence_interval: 'daily',
  recurrence_days: null,
  recurrence_end_date: null,
  owner_id: null,
}

const localData = ref({ ...defaultFormData })

// --- COMBINED FILTERING LOGIC ---

const departmentFilter = ref('');
const teamFilter = ref('');

const roleHierarchy = {
  'SM': 4,
  'HR': 4,
  'Director': 3,
  'Manager': 2,
  'Staff': 1
};

const hierarchicalUsers = computed(() => {
  const currentUserRole = authStore.user?.role;
  const currentUserId = authStore.user?.id;
  
  if (!currentUserRole || !currentUserId || !props.allUsers.length) return [];
  
  const currentUserRank = roleHierarchy[currentUserRole] || 0;

  return props.allUsers.filter(user => {
    const userRank = roleHierarchy[user.role] || 0;
    return user.id !== currentUserId && userRank < currentUserRank;
  });
});

const departments = computed(() => {
  const allDepts = hierarchicalUsers.value.map(user => user.department).filter(Boolean);
  return [...new Set(allDepts)];
});

const teams = computed(() => {
  let relevantUsers = hierarchicalUsers.value;
  if (departmentFilter.value) {
    relevantUsers = relevantUsers.filter(user => user.department === departmentFilter.value);
  }
  const allTeams = relevantUsers.map(user => user.team).filter(Boolean);
  return [...new Set(allTeams)];
});

watch(departmentFilter, () => {
  teamFilter.value = '';
});

const filteredUsers = computed(() => {
  let users = hierarchicalUsers.value;

  if (departmentFilter.value) {
    users = users.filter(user => user.department === departmentFilter.value);
  }

  if (teamFilter.value) {
    users = users.filter(user => user.team === teamFilter.value);
  }

  return users;
});
// --- END COMBINED LOGIC ---

const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  // Construct the string in the required format YYYY-MM-DDTHH:mm
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

// --- CORRECTED MINIMUM DEADLINE LOGIC ---
const minDeadline = computed(() => {
  // If we are editing a task AND that task already has a deadline,
  // the minimum should be that existing deadline.
  if (isEditMode.value && localData.value.deadline) {
    return localData.value.deadline;
  }
  // Otherwise (for new tasks), the minimum is the current time.
  return formatDateForInput(new Date());
});
// --- END CORRECTION ---

const minRecurrenceEndDate = computed(() => {
  return localData.value.deadline || minDeadline.value;
});

watch(() => props.taskToEdit, (task) => {
  if (task) {
    localData.value = {
      id: task.id,
      title: task.title || '',
      description: task.description || '',
      deadline: formatDateForInput(task.deadline),
      status: task.status || 'Unassigned',
      priority: task.priority || 5,
      is_recurring: task.is_recurring || false,
      recurrence_interval: task.recurrence_interval || 'daily',
      recurrence_days: task.recurrence_days || null,
      recurrence_end_date: formatDateForInput(task.recurrence_end_date),
      owner_id: task.owner_id,
    }
  } else {
    localData.value = { ...defaultFormData }
  }
}, { immediate: true })

watch(() => localData.value.deadline, (newDeadline) => {
  if (localData.value.recurrence_end_date && newDeadline > localData.value.recurrence_end_date) {
    localData.value.recurrence_end_date = newDeadline;
  }
});

const handleSubmit = () => {
  if (!localData.value.title.trim()) {
    alert('Please fill in a Title for the task.')
    return
  }
  emit('submit', { ...localData.value })
  if (!isEditMode.value) {
    localData.value = { ...defaultFormData }
  }
}
</script>