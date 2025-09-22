<template>
  <div class="p-6 max-w-5xl mx-auto">
    <!-- Task Details -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h1 class="text-2xl font-bold mb-2">{{ task.title }}</h1>
      <p class="text-gray-600 mb-4">{{ task.description }}</p>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <p><span class="font-semibold">Status:</span> {{ task.status }}</p>
          <p><span class="font-semibold">Deadline:</span> {{ task.deadline || 'N/A' }}</p>
        </div>
        <div>
          <p><span class="font-semibold">Owner ID:</span> {{ task.owner_id }}</p>
        </div>
      </div>
    </div>

    <!-- Subtasks -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Subtasks</h2>
      <ul>
        <li
          v-for="sub in task.subtasks"
          :key="sub.id"
          class="border-b py-2 flex justify-between items-center"
        >
          <span>{{ sub.title }}</span>
          <span class="text-sm text-gray-500">{{ sub.status }}</span>
        </li>
        <li v-if="task.subtasks.length === 0" class="text-gray-500">No subtasks yet.</li>
      </ul>
    </div>

    <!-- Comments -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Comments</h2>
      <ul>
        <li
          v-for="comment in task.comments"
          :key="comment.id"
          class="border-b py-2"
        >
          <p class="text-gray-800">{{ comment.body }}</p>
          <p class="text-sm text-gray-500">Author ID: {{ comment.author_id }}</p>
        </li>
        <li v-if="task.comments.length === 0" class="text-gray-500">No comments yet.</li>
      </ul>
    </div>

    <!-- Attachments -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">Attachments</h2>
      <ul>
        <li
          v-for="att in task.attachments"
          :key="att.id"
          class="py-2"
        >
          <a :href="att.url" target="_blank" class="text-indigo-600 hover:underline">
            {{ att.filename }}
          </a>
        </li>
        <li v-if="task.attachments.length === 0" class="text-gray-500">No attachments.</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
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

const KONG_API_URL = "http://localhost:6001"; 
const token = localStorage.getItem('authToken');

onMounted(async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) throw new Error('Failed to fetch task details');

    task.value = await response.json();
  } catch (err) {
    console.error('Error loading task details:', err);
  }
});
</script>

<style scoped>

</style>
