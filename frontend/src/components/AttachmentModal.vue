<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-[100]" @click.self="$emit('close')">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        
        <div class="flex justify-between items-center pb-3 border-b border-gray-200">
          <h3 class="text-xl font-semibold text-gray-900">Upload Attachment</h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div class="mt-4">
          <form @submit.prevent="submitAttachment">
            
            <div class="mb-4">
              <label for="attachment-name" class="block text-sm font-medium text-gray-700 mb-2">
                Attachment Name
              </label>
              <input
                id="attachment-name"
                v-model="fileName"
                type="text"
                placeholder="e.g., Final Report Q3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div class="mb-6">
            <label for="file-upload" class="block text-sm font-medium text-gray-700 mb-2">
                Select File
            </label>

            <!-- Hide the native input -->
            <input
                id="file-upload"
                type="file"
                class="hidden"
                @change="handleFileChange"
                ref="fileInputRef"
            />

            <!-- Custom styled button -->
            <label
                for="file-upload"
                class="inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg cursor-pointer hover:bg-indigo-700"
            >
                Choose File
            </label>

            <!-- Show selected file name -->
            <p v-if="file" class="mt-2 text-sm text-gray-500">
                Selected: {{ file.name }}
            </p>
            <p v-else class="mt-2 text-sm text-gray-500 italic">
                No file selected.
            </p>
            </div>

            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="$emit('close')"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-300 transition duration-150 ease-in-out cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="!file || isUploading"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 ease-in-out cursor-pointer"
              >
                <span v-if="isUploading">Uploading...</span>
                <span v-else>Upload</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  taskId: {
    type: [String, Number],
    required: true,
  },
  isUploading: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['close', 'upload']);

const fileName = ref('');
const file = ref(null);

// Reset form fields when the modal is closed
watch(() => props.show, (newVal) => {
  if (!newVal) {
    fileName.value = '';
    file.value = null;
  }
});

const handleFileChange = (event) => {
  const newFile = event.target.files ? event.target.files[0] : null;
  if (newFile) {
    file.value = newFile;
    fileName.value = newFile.name; 
  } 
};

const submitAttachment = () => {
  if (file.value) {
    const data = {
      file: file.value,
      // Use the name from the input, or fall back to the original file name
      name: fileName.value.trim() || file.value.name, 
      taskId: props.taskId
    };
    emit('upload', data);
  }
};
</script>

<style scoped>
/* Basic transition for the modal effect */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>