<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 backdrop-blur-sm" @click="$emit('close')"></div>

      <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg relative z-10">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900">Edit Project</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <div v-if="successMessage" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-700">{{ successMessage }}</p>
        </div>

        <form @submit.prevent="saveProjectChanges" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Project Title *</label>
            <input v-model="editedProject.title" type="text" required
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="editedProject.description" rows="4"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
            <input v-model="editedProject.deadline" type="datetime-local"
                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          </div>

          <div class="border-t pt-6">
            <label class="block text-sm font-medium text-gray-700">Owner</label>
            <p class="text-xs text-gray-500 mt-1">
              Currently owned by: {{ ownerDetails ? ownerDetails.name : `User ${project?.owner_id}` }}.
            </p>
          </div>

          <div class="border-t pt-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Manage Collaborators</label>
            
            <div class="space-y-2 mb-4 max-h-40 overflow-y-auto p-2 border border-gray-200 rounded-md bg-gray-50">
              <div v-if="collaboratorDetails.length === 0" class="text-sm text-gray-500 text-center py-2">No collaborators added yet.</div>
              <div v-for="collaborator in collaboratorDetails" :key="collaborator.user_id" class="flex items-center justify-between p-2 bg-white rounded-md shadow-sm border border-gray-100">
                <span class="text-sm font-medium text-gray-800">{{ collaborator.name }} ({{ collaborator.role }})</span>
                <button @click="removeCollaborator(collaborator.user_id)" type="button" title="Remove Collaborator" :disabled="!isOwner" class="text-red-500 hover:text-red-700 text-xs font-semibold p-1 rounded-full hover:bg-red-50 transition disabled:text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
              </div>
            </div>
            
            <div v-if="isOwner">
              <div class="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <label class="block text-xs text-gray-500">Filter by Department</label>
                  <select v-model="collaboratorDepartmentFilter" class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border">
                    <option value="">All Departments</option>
                    <option v-for="dept in collaboratorDepartments" :key="dept" :value="dept">
                      {{ dept }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs text-gray-500">Filter by Team</label>
                  <select v-model="collaboratorTeamFilter" class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border">
                    <option value="">All Teams</option>
                    <option v-for="team in collaboratorTeams" :key="team" :value="team">
                      {{ team }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="flex items-center space-x-2">
                <select v-model="selectedCollaboratorId" class="flex-grow border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2 border">
                  <option :value="null" disabled>Select a user to add ({{ availableCollaborators.length }} available)...</option>
                  <option v-for="user in availableCollaborators" :key="user.id" :value="user.id">
                    {{ user.name }} ({{ user.role }})
                  </option>
                </select>
                <button @click="addCollaborator" type="button" :disabled="!selectedCollaboratorId" class="flex-shrink-0 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-md text-sm font-medium disabled:opacity-50 transition duration-150">
                  Add
                </button>
              </div>
            </div>
             <p v-else class="text-xs text-gray-500 mt-1">Only the project owner can add or remove collaborators.</p>
          </div>

          <div class="mt-6 flex justify-end space-x-3 pt-6 border-t">
            <button type="button" @click="$emit('close')"
                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  show: Boolean,
  project: Object
});

const emit = defineEmits(['close', 'updated']);

const authStore = useAuthStore();
const KONG_API_URL = "http://localhost:8000";

// --- Form State ---
const saving = ref(false);
const error = ref(null);
const successMessage = ref(null);
const allUsers = ref([]); // Store all users for filters
const ownerDetails = ref(null); // Store fetched owner details

const editedProject = ref({
  title: '',
  description: '',
  deadline: '',
  // owner_id removed
});

// --- Collaborator State ---
const selectedCollaboratorId = ref(null);
const originalCollaboratorIds = ref(new Set()); // To track original state
const localCollaborators = ref([]); // Stores just the IDs
const collaboratorDetails = ref([]); // Stores { user_id, name, role }
const collaboratorDepartmentFilter = ref('');
const collaboratorTeamFilter = ref('');

// --- Owner Transfer State Removed ---

// --- Computed Properties ---
const isOwner = computed(() => props.project?.owner_id === authStore.currentUserId);

// --- Owner Transfer Computed Properties Removed ---

// --- Collaborator Computed Properties ---
const collaboratorDepartments = computed(() => {
  const depts = allUsers.value.map(u => u.department).filter(Boolean);
  return [...new Set(depts)];
});

const collaboratorTeams = computed(() => {
  let users = allUsers.value;
  if (collaboratorDepartmentFilter.value) {
    users = users.filter(u => u.department === collaboratorDepartmentFilter.value);
  }
  const teams = users.map(u => u.team).filter(Boolean);
  return [...new Set(teams)];
});

const availableCollaborators = computed(() => {
  const currentIds = new Set(localCollaborators.value);
  const ownerId = props.project?.owner_id;
  currentIds.add(ownerId); // Cannot add owner as collaborator

  let users = allUsers.value.filter(u => !currentIds.has(u.id));

  if (collaboratorDepartmentFilter.value) {
    users = users.filter(u => u.department === collaboratorDepartmentFilter.value);
  }
  if (collaboratorTeamFilter.value) {
    users = users.filter(u => u.team === collaboratorTeamFilter.value);
  }
  return users;
});


// --- Helper Functions ---
const fetchUserDetails = async (userId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/user/${userId}`);
    if (response.ok) {
      const data = await response.json();
      return { user_id: userId, name: data.name || `User ${userId}`, role: data.role || 'N/A' };
    }
    console.warn(`Failed to fetch details for user ${userId}`);
    return { user_id: userId, name: `User ${userId}`, role: 'N/A' }; // Fallback
  } catch (err) {
    console.error(`Error fetching user ${userId}:`, err);
    return { user_id: userId, name: `User ${userId}`, role: 'N/A' }; // Fallback
  }
};

const fetchAllUsers = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/user`);
    if (response.ok) {
      allUsers.value = await response.json();
    } else {
      console.error("Failed to fetch all users.");
    }
  } catch (err) {
    console.error("Error fetching all users:", err);
  }
};

const fetchCollaboratorDetails = async (collaboratorIds) => {
    if (!collaboratorIds || collaboratorIds.length === 0) {
        collaboratorDetails.value = [];
        return;
    }
    try {
        if (allUsers.value.length > 0) {
             collaboratorDetails.value = collaboratorIds.map(id => {
                const user = allUsers.value.find(u => u.id === id);
                return {
                    user_id: id,
                    name: user?.name || `User ${id}`,
                    role: user?.role || 'N/A'
                };
             });
        } else {
            const detailsPromises = collaboratorIds.map(id => fetchUserDetails(id));
            collaboratorDetails.value = await Promise.all(detailsPromises);
        }
    } catch (err) {
        console.error("Error fetching collaborator details:", err);
        collaboratorDetails.value = collaboratorIds.map(id => ({ user_id: id, name: `User ${id}`, role: 'N/A' }));
    }
};

// --- Watchers ---
watch(() => props.project, async (newProject) => {
  if (newProject) {
    editedProject.value = {
      title: newProject.title,
      description: newProject.description || '',
      deadline: newProject.deadline ? newProject.deadline.slice(0, 16) : '',
      // owner_id removed
    };
    
    const collaboratorIds = newProject.collaborator_ids || [];
    originalCollaboratorIds.value = new Set(collaboratorIds); 
    localCollaborators.value = [...collaboratorIds];          
    
    if (allUsers.value.length === 0) {
        await fetchAllUsers();
    }
    fetchCollaboratorDetails(localCollaborators.value);
    
    if (newProject.owner_id) {
        const owner = allUsers.value.find(u => u.id === newProject.owner_id);
        if(owner) {
            ownerDetails.value = { user_id: owner.id, name: owner.name, role: owner.role };
        } else {
            ownerDetails.value = await fetchUserDetails(newProject.owner_id);
        }
    }
  } else {
    // Reset
    editedProject.value = { title: '', description: '', deadline: '' }; // owner_id removed
    originalCollaboratorIds.value = new Set();
    localCollaborators.value = [];
    collaboratorDetails.value = [];
    ownerDetails.value = null;
  }
}, { immediate: true });

// Watchers for filters
// departmentFilter watch removed
watch(collaboratorDepartmentFilter, () => {
  collaboratorTeamFilter.value = '';
});

// --- Methods ---
const saveProjectChanges = async () => {
  try {
    saving.value = true;
    error.value = null;
    successMessage.value = null;

    // --- 1. Calculate Field Changes ---
    const changes = {};
    if (editedProject.value.title !== props.project.title) {
      changes.title = editedProject.value.title;
    }
    if (editedProject.value.description !== (props.project.description || '')) {
      changes.description = editedProject.value.description;
    }
    const currentDeadline = props.project.deadline ? props.project.deadline.slice(0, 16) : '';
    const newDeadline = editedProject.value.deadline || null;
    if (newDeadline !== currentDeadline) {
      changes.deadline = newDeadline;
    }
    // owner_id change logic removed

    // --- 2. Calculate Collaborator Changes ---
    const originalIds = originalCollaboratorIds.value; 
    const finalIds = new Set(localCollaborators.value);    
    
    const collaborators_to_add = [...finalIds].filter(id => !originalIds.has(id));
    const collaborators_to_remove = [...originalIds].filter(id => !finalIds.has(id));

    if (collaborators_to_add.length > 0) {
      changes.collaborators_to_add = collaborators_to_add;
    }
    if (collaborators_to_remove.length > 0) {
      changes.collaborators_to_remove = collaborators_to_remove;
    }

    // --- 3. Check if any changes exist ---
    if (Object.keys(changes).length === 0) {
        successMessage.value = 'No changes detected.';
        setTimeout(() => { emit('close'); successMessage.value = null; }, 1500);
        saving.value = false;
        return; 
    }

    // --- 4. Send Payload ---
    const payload = {
      ...changes,
      user_id: authStore.currentUserId 
    };

    const response = await fetch(`${KONG_API_URL}/projects/${props.project.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update project details');
    }

    successMessage.value = 'Project details updated successfully!';
    setTimeout(() => {
      emit('updated'); 
      emit('close');
    }, 1000);

  } catch (err) {
    console.error('Error saving project changes:', err);
    error.value = err.message;
  } finally {
    saving.value = false;
  }
};

// --- MODIFIED (FIXED) ---
const addCollaborator = () => {
  if (!isOwner.value || !selectedCollaboratorId.value) return;

  const collaboratorIdToAdd = selectedCollaboratorId.value;
  
  if (!localCollaborators.value.includes(collaboratorIdToAdd)) {
    
    const userToAdd = allUsers.value.find(u => u.id === collaboratorIdToAdd);

    if (userToAdd) {
      localCollaborators.value.push(collaboratorIdToAdd);
      collaboratorDetails.value.push({
        user_id: userToAdd.id,
        name: userToAdd.name,
        role: userToAdd.role
      });
    } else {
      console.warn(`User with ID ${collaboratorIdToAdd} not found in allUsers list.`);
    }
  }
  
  selectedCollaboratorId.value = null; 
  error.value = null;
  successMessage.value = null;
};

const removeCollaborator = (collaboratorIdToRemove) => {
   if (!isOwner.value) return;
   
   if (!confirm(`Remove this user from the project? This change will be saved when you click 'Save Changes'.`)) return;

  localCollaborators.value = localCollaborators.value.filter(id => id !== collaboratorIdToRemove);
  collaboratorDetails.value = collaboratorDetails.value.filter(detail => detail.user_id !== collaboratorIdToRemove);

  error.value = null;
  successMessage.value = null;
};

// Lifecycle Hooks
onMounted(() => {
    if (allUsers.value.length === 0) {
        fetchAllUsers();
    }
});
</script>