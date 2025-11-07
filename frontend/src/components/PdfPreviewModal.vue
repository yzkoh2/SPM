<template>
  <div
    class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center p-4"
  >
    <div class="relative bg-white rounded-lg shadow-xl w-full max-w-4xl h-[90vh] flex flex-col">
      <div class="flex justify-between items-center p-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Report Preview</h3>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600 transition-colors"
          title="Close"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <div class="flex-grow p-4 bg-gray-50">
        <iframe v-if="pdfUrl" :src="pdfUrl" class="w-full h-full border border-gray-300 rounded-md">
          Your browser does not support PDFs. Please download the file to view it.
        </iframe>
        <div v-else class="flex justify-center items-center h-full">
          <p class="text-gray-500">Loading PDF preview...</p>
        </div>
      </div>

      <div class="flex justify-between items-center p-4 border-t border-gray-200">
        <div class="flex items-center text-sm text-green-600">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span>Report successfully saved to your history</span>
        </div>

        <div class="space-x-3">
          <button
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Close
          </button>
          <a
            :href="pdfUrl"
            :download="filename"
            class="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors inline-flex items-center"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              ></path>
            </svg>
            Download PDF
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pdfUrl: {
    type: String,
    required: true,
  },
  filename: {
    type: String,
    default: 'report.pdf',
  },
})

defineEmits(['close'])
</script>