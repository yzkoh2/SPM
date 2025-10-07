<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="$emit('close')"></div>

      <!-- Modal panel - FIXED: Added relative z-10 -->
      <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg relative z-10">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-900">Edit Project</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
          <p class="text-sm text-green-700">{{ successMessage }}</p>
        </div>

        <!-- Tabs -->
        <div class="border-b border-gray-200 mb-6">
          <nav class="-mb-px flex space-x-8">
            <button @click="activeTab = 'details'"
                    :class="[activeTab === 'details' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
              Project Details
            </button>
            <button @click="activeTab = 'collaborators'"
                    :class="[activeTab === 'collaborators' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm']">
              Collaborators
            </button>
          </nav>
        </div>

        <!-- Project Details Tab -->
        <div v-if="activeTab === 'details'">
          <form @submit.prevent="saveProjectDetails">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
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
            </div>

            <div class="mt-6 flex justify-end space-x-3">
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

        <!-- Collaborators Tab -->
        <div v-if="activeTab === 'collaborators'">
          <div class="space-y-4">
            <!-- Add Collaborator -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Add Collaborator</h4>
              <div class="flex space-x-2">
                <input v-model.number="newCollaboratorId" type="number" placeholder="Enter User ID"
                       class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
                <button @click="addCollaborator" :disabled="adding || !newCollaboratorId"
                        class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400">
                  {{ adding ? 'Adding...' : 'Add' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-2">Enter the user ID of the person you want to add as a collaborator</p>
            </div>

            <!-- Current Collaborators -->
            <div>
              <h4 class="text-sm font-medium text-gray-900 mb-3">Current Collaborators</h4>
              
              <!-- Owner -->
              <div class="flex items-center justify-between p-3 bg-indigo-50 rounded-lg mb-2">
                <div class="flex items-center">
                  <div class="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center mr-3">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">User {{ project.owner_id }}</p>
                    <p class="text-xs text-indigo-600 font-medium">Owner</p>
                  </div>
                </div>
                <span class="text-xs text-gray-500">Cannot be removed</span>
              </div>

              <!-- Collaborators List -->
              <div v-if="localCollaborators.length > 0" class="space-y-2">
                <div v-for="collaboratorId in localCollaborators" :key="collaboratorId"
                     class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg">
                  <div class="flex items-center">
                    <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mr-3">
                      <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">User {{ collaboratorId }}</p>
                      <p class="text-xs text-gray-500">Collaborator</p>
                    </div>
                  </div>
                  <button @click="removeCollaborator(collaboratorId)" 
                          :disabled="removing === collaboratorId"
                          class="text-red-600 hover:text-red-800 text-sm font-medium disabled:text-gray-400">
                    {{ removing === collaboratorId ? 'Removing...' : 'Remove' }}
                  </button>
                </div>
              </div>

              <!-- No Collaborators -->
              <div v-else class="text-center py-6 text-gray-500 text-sm">
                No collaborators yet. Add one above!
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: Boolean,
  project: Object
})

const emit = defineEmits(['close', 'updated'])

const authStore = useAuthStore()
const KONG_API_URL = "http://localhost:8000"

const activeTab = ref('details')
const saving = ref(false)
const adding = ref(false)
const removing = ref(null)
const error = ref(null)
const successMessage = ref(null)

const editedProject = ref({
  title: '',
  description: '',
  deadline: ''
})

const newCollaboratorId = ref(null)
const localCollaborators = ref([])

// Watch for project prop changes
watch(() => props.project, (newProject) => {
  if (newProject) {
    editedProject.value = {
      title: newProject.title,
      description: newProject.description || '',
      deadline: newProject.deadline ? newProject.deadline.slice(0, 16) : ''
    }
    localCollaborators.value = [...(newProject.collaborator_ids || [])]
  }
}, { immediate: true })

const saveProjectDetails = async () => {
  try {
    saving.value = true
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/projects/${props.project.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...editedProject.value,
        user_id: authStore.currentUserId
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to update project')
    }

    successMessage.value = 'Project updated successfully!'
    
    setTimeout(() => {
      emit('updated')
      emit('close')
    }, 1000)

  } catch (err) {
    console.error('Error updating project:', err)
    error.value = err.message
  } finally {
    saving.value = false
  }
}

const addCollaborator = async () => {
  try {
    adding.value = true
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/projects/${props.project.id}/collaborators`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: authStore.currentUserId,
        collaborator_user_id: newCollaboratorId.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add collaborator')
    }

    localCollaborators.value.push(newCollaboratorId.value)
    newCollaboratorId.value = null
    successMessage.value = 'Collaborator added successfully!'
    setTimeout(() => successMessage.value = null, 3000)

  } catch (err) {
    console.error('Error adding collaborator:', err)
    error.value = err.message
  } finally {
    adding.value = false
  }
}

const removeCollaborator = async (collaboratorId) => {
  if (!confirm(`Remove User ${collaboratorId} from project? They will also be removed from all project tasks.`)) {
    return
  }

  try {
    removing.value = collaboratorId
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/projects/${props.project.id}/collaborators/${collaboratorId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: authStore.currentUserId
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to remove collaborator')
    }

    localCollaborators.value = localCollaborators.value.filter(id => id !== collaboratorId)
    successMessage.value = 'Collaborator removed from project and all tasks!'
    setTimeout(() => successMessage.value = null, 3000)

  } catch (err) {
    console.error('Error removing collaborator:', err)
    error.value = err.message
  } finally {
    removing.value = null
  }
}
</script>