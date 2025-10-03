<template>
  <div v-if="task" class="bg-white rounded-lg shadow-lg overflow-hidden">
    <div class="p-6 border-b border-gray-200">
      <h2 class="text-2xl font-bold text-gray-900">{{ task.title }}</h2>
      <p class="text-sm text-gray-600 mt-1">Owner ID: {{ task.owner_id }}</p>
      <span
        class="mt-4 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
        :class="statusBadgeColor"
      >
        {{ task.status }}
      </span>
    </div>

    <div class="p-6">
      <div>
        <h3 class="text-lg font-semibold text-gray-800">Description</h3>
        <p class="mt-2 text-gray-700 whitespace-pre-wrap">{{ task.description || 'No description provided.' }}</p>
      </div>

      <div class="mt-6">
        <h3 class="text-lg font-semibold text-gray-800">Details</h3>
        <div class="mt-2 border-t border-b border-gray-200 divide-y divide-gray-200">
          <div class="py-3 flex justify-between text-sm">
            <span class="font-medium text-gray-600">Deadline</span>
            <span :class="deadlineColor">{{ formatDeadline(task.deadline) }}</span>
          </div>
          </div>
      </div>

      <slot name="subtasks"></slot>
      <slot name="comments"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  task: {
    type: Object,
    default: () => null
  }
});

// (Reusing computed properties from TaskCard for consistency)
const statusBadgeColor = computed(() => {
  if (!props.task) return '';
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    'Completed': 'bg-green-100 text-green-800'
  };
  return colors[props.task.status] || 'bg-gray-100 text-gray-800';
});

const deadlineColor = computed(() => {
  if (!props.task || !props.task.deadline) return 'text-gray-700';
  const now = new Date();
  const deadlineDate = new Date(props.task.deadline);
  if (deadlineDate < now) return 'text-red-600 font-bold';
  return 'text-gray-900';
});

const formatDeadline = (deadline) => {
  if (!deadline) return 'Not set';
  return new Date(deadline).toLocaleString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};
</script>