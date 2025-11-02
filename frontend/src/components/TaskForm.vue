<template>
  <div class="bg-white rounded-lg shadow-md p-6 m-8">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">{{ formTitle }}</h2>
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ isSubtask ? 'Subtask Title' : 'Task Title' }}
        </label>
        <input
          v-model="localData.title"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Deadline</label>
        <input
          v-model="localData.deadline"
          type="datetime-local"
          :min="minDeadline"
          :max="maxDeadline"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          required
        />
        <p
          v-if="isSubtask && maxDeadline && localData.deadline > maxDeadline"
          class="mt-2 text-sm text-red-600"
        >
          ⚠️ The subtask deadline cannot be past the parent task's deadline.
        </p>

        <p
          v-if="localData.deadline && localData.deadline < minDeadline"
          class="mt-2 text-sm text-red-600"
        >
          ⚠️ The task deadline cannot be earlier than the current date and time.
        </p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <textarea
          v-model="localData.description"
          rows="3"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="Describe the task in detail..."
          required
        ></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
        <select
          v-model="localData.status"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        >
          <option value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Priority</label>
        <input
          v-model="localData.priority"
          type="range"
          min="1"
          max="10"
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div class="flex justify-between text-xs text-gray-600 mt-1">
          <span v-for="n in 10" :key="n">{{ n }}</span>
        </div>
      </div>

      <div>
        <label class="flex items-center">
          <input
            v-model="localData.is_recurring"
            type="checkbox"
            class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          />
          <span class="ml-2 text-sm text-gray-600">Is this a recurring task?</span>
        </label>
      </div>

      <div v-if="localData.is_recurring">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence Interval</label>
          <select
            v-model="localData.recurrence_interval"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div v-if="localData.recurrence_interval === 'custom'">
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence Days</label>
          <input
            v-model="localData.recurrence_days"
            type="number"
            min="1"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recurrence End Date</label>
          <input
            v-model="localData.recurrence_end_date"
            type="datetime-local"
            :min="minRecurrenceEndDate"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
      </div>

      <div v-if="isEditMode && hierarchicalUsers.length > 0" class="border-t pt-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Assign New Owner</label>
        <div class="grid grid-cols-2 gap-4 mb-3">
          <div>
            <label class="block text-xs text-gray-500">Filter by Department</label>
            <select
              v-model="departmentFilter"
              class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
            >
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept" :value="dept">
                {{ dept }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-500">Filter by Team</label>
            <select
              v-model="teamFilter"
              class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
            >
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

      <div class="border-t pt-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Manage Collaborators</label>

        <div class="space-y-2 mb-4">
          <div v-if="localCollaborators.length === 0" class="text-sm text-gray-500">
            No collaborators added yet.
          </div>
          <div
            v-for="collaborator in localCollaborators"
            :key="collaborator.user_id"
            class="flex items-center justify-between p-2 bg-gray-50 rounded-md"
          >
            <span class="text-sm font-medium text-gray-800"
              >{{ collaborator.name }} ({{ collaborator.role }})</span
            >
            <button
              v-if="collaborator.user_id !== (taskToEdit ? taskToEdit.owner_id : authStore.user.id)"
              @click="removeCollaborator(collaborator.user_id)"
              type="button"
              class="text-red-500 hover:text-red-700 text-xs font-semibold"
            >
              Remove
            </button>
            <span v-else class="text-xs text-gray-400 font-medium">(Owner)</span>
          </div>
        </div>

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
            <label class="block text-xs text-gray-500">Filter by Team</label>
            <select
              v-model="collaboratorTeamFilter"
              class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
            >
              <option value="">All Teams</option>
              <option v-for="team in collaboratorTeams" :key="team" :value="team">
                {{ team }}
              </option>
            </select>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <select
            v-model="selectedCollaboratorId"
            class="flex-grow border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border"
          >
            <option :value="null" disabled>Select a user to add...</option>
            <option v-for="user in availableCollaborators" :key="user.id" :value="user.id">
              {{ user.name }} ({{ user.role }})
            </option>
          </select>
          <button
            @click="addCollaborator"
            type="button"
            :disabled="!selectedCollaboratorId"
            class="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-md text-sm font-medium disabled:opacity-50"
          >
            Add
          </button>
        </div>
      </div>

      <div class="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors disabled:opacity-50"
        >
          {{ isSubmitting ? submitButtonLoadingText : submitButtonText }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, computed, watchEffect } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const props = defineProps({
  isSubtask: { type: Boolean, default: false },
  isSubmitting: { type: Boolean, default: false },
  submitButtonText: { type: String, default: 'Create Task' },
  submitButtonLoadingText: { type: String, default: 'Creating...' },
  taskToEdit: { type: Object, default: null },
  allUsers: { type: Array, default: () => [] },
  currentCollaborators: { type: Array, default: () => [] },
  parentDeadline: { type: String, default: null },
})

const emit = defineEmits(['submit', 'cancel'])

const isEditMode = computed(() => !!props.taskToEdit)
const formTitle = computed(() =>
  isEditMode.value
    ? props.isSubtask
      ? 'Edit Subtask'
      : 'Edit Task'
    : props.isSubtask
      ? 'Create New Subtask'
      : 'Create New Task',
)

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
const localCollaborators = ref([])
const selectedCollaboratorId = ref(null)

// --- COLLABORATOR LOGIC ---

watch(
  () => props.taskToEdit,
  (newTask) => {
    if (newTask && isEditMode.value) {
      // Set the initial state ONCE when a task is loaded for editing
      const initialCollabs = JSON.parse(JSON.stringify(props.currentCollaborators || []))
      localCollaborators.value = initialCollabs
    } else {
      // Reset for a new task form (create mode)
      localCollaborators.value = []
    }
  },
  { immediate: true },
)

const collaboratorDepartmentFilter = ref('')
const collaboratorTeamFilter = ref('')

const collaboratorDepartments = computed(() => {
  const depts = props.allUsers.map((u) => u.department).filter(Boolean)
  return [...new Set(depts)]
})

const collaboratorTeams = computed(() => {
  let users = props.allUsers
  if (collaboratorDepartmentFilter.value) {
    users = users.filter((u) => u.department === collaboratorDepartmentFilter.value)
  }
  const teams = users.map((u) => u.team).filter(Boolean)
  return [...new Set(teams)]
})

watch(collaboratorDepartmentFilter, () => {
  collaboratorTeamFilter.value = ''
})

const availableCollaborators = computed(() => {
  const currentIds = new Set(localCollaborators.value.map((c) => c.user_id))
  const ownerId = isEditMode.value ? props.taskToEdit.owner_id : authStore.user.id
  currentIds.add(ownerId)

  let users = props.allUsers.filter((u) => !currentIds.has(u.id))

  if (collaboratorDepartmentFilter.value) {
    users = users.filter((u) => u.department === collaboratorDepartmentFilter.value)
  }
  if (collaboratorTeamFilter.value) {
    users = users.filter((u) => u.team === collaboratorTeamFilter.value)
  }
  return users
})

function addCollaborator() {
  if (!selectedCollaboratorId.value) return

  const userToAdd = props.allUsers.find((u) => u.id === selectedCollaboratorId.value)
  if (userToAdd) {
    localCollaborators.value.push({
      user_id: userToAdd.id,
      name: userToAdd.name,
      role: userToAdd.role,
    })
  }
  selectedCollaboratorId.value = null
}

function removeCollaborator(userId) {
  localCollaborators.value = localCollaborators.value.filter((c) => c.user_id !== userId)
}

// --- Owner Transfer Logic ---
const departmentFilter = ref('')
const teamFilter = ref('')
const roleHierarchy = { SM: 4, HR: 4, Director: 3, Manager: 2, Staff: 1 }

const hierarchicalUsers = computed(() => {
  const currentUserRole = authStore.user?.role
  const currentUserId = authStore.user?.id
  if (!currentUserRole || !currentUserId || !props.allUsers.length) return []
  const currentUserRank = roleHierarchy[currentUserRole] || 0
  return props.allUsers.filter((user) => {
    const userRank = roleHierarchy[user.role] || 0
    return user.id !== currentUserId && userRank < currentUserRank
  })
})

const departments = computed(() => {
  const allDepts = hierarchicalUsers.value.map((user) => user.department).filter(Boolean)
  return [...new Set(allDepts)]
})

const teams = computed(() => {
  let relevantUsers = hierarchicalUsers.value
  if (departmentFilter.value) {
    relevantUsers = relevantUsers.filter((user) => user.department === departmentFilter.value)
  }
  const allTeams = relevantUsers.map((user) => user.team).filter(Boolean)
  return [...new Set(allTeams)]
})

watch(departmentFilter, () => {
  teamFilter.value = ''
})

const filteredUsers = computed(() => {
  let users = hierarchicalUsers.value
  if (departmentFilter.value) {
    users = users.filter((user) => user.department === departmentFilter.value)
  }
  if (teamFilter.value) {
    users = users.filter((user) => user.team === teamFilter.value)
  }
  return users
})

// --- Date Formatting and Logic ---

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

const isOverdue = computed(() => {
  if (!isEditMode.value || !localData.value.deadline) {
    return false
  }
  const currentDeadline = new Date(localData.value.deadline).getTime()
  const now = new Date().getTime()
  // Use an hour buffer for comparison, in case of small time drift
  return currentDeadline < now - 60 * 60 * 1000
})

const minDeadline = computed(() => {
  // if (isEditMode.value && localData.value.deadline) {
  //   return localData.value.deadline;
  // }
  if (isEditMode.value && isOverdue.value) {
    // Allow the user to keep the existing (past) deadline.
    return localData.value.deadline
  }
  return formatDateForInput(new Date())
})

const minRecurrenceEndDate = computed(() => {
  const baseDate = localData.value.deadline || minDeadline.value

  const date = new Date(baseDate)
  date.setDate(date.getDate() + 1)

  return formatDateForInput(date)
})

const maxDeadline = computed(() => {
  if (props.isSubtask && props.parentDeadline) {
    return props.parentDeadline
  }
  return null
})

// --- Watchers ---

watch(
  () => props.taskToEdit,
  (task) => {
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
  },
  { immediate: true },
)

watch(
  () => localData.value.deadline,
  (newDeadline) => {
    if (localData.value.recurrence_end_date && newDeadline > localData.value.recurrence_end_date) {
      localData.value.recurrence_end_date = newDeadline
    }
  },
)

// --- Form Submission ---

const handleSubmit = () => {
  if (!localData.value.title.trim()) {
    alert('Please fill in a Title for the task.')
    return
  }

  // Calculate collaborator changes for the final payload
  const initialIds = new Set((props.currentCollaborators || []).map((c) => c.user_id))
  const finalIds = new Set(localCollaborators.value.map((c) => c.user_id))

  const collaborators_to_add = [...finalIds].filter((id) => !initialIds.has(id))
  const collaborators_to_remove = [...initialIds].filter((id) => !finalIds.has(id))

  // Convert datetime-local to ISO string with timezone
  const payload = {
    ...localData.value,
    collaborators_to_add,
    collaborators_to_remove,
  }

  // Convert deadline to ISO string with timezone if present
  if (payload.deadline) {
    const deadlineDate = new Date(payload.deadline)
    payload.deadline = deadlineDate.toISOString()
    payload.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  }

  // Convert recurrence_end_date to ISO string with timezone if present
  if (payload.recurrence_end_date) {
    const recurrenceEndDate = new Date(payload.recurrence_end_date)
    payload.recurrence_end_date = recurrenceEndDate.toISOString()
  }

  emit('submit', payload)
}
</script>
