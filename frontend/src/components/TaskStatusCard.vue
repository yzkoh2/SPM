<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center">
      <div :class="iconBgClass" class="p-2 rounded-lg">
        <svg
          :class="iconColorClass"
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            v-if="icon === 'clipboard'"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          ></path>
          <path
            v-else-if="icon === 'clock'"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
          <path
            v-else-if="icon === 'spinner'"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          ></path>
          <path
            v-else-if="icon === 'check'"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          ></path>
        </svg>
      </div>
      <div class="ml-4">
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-2xl font-semibold text-gray-900">{{ count }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  count: {
    type: Number,
    required: true,
  },
  icon: {
    type: String,
    required: true,
    validator: (value) => ['clipboard', 'clock', 'spinner', 'check'].includes(value),
  },
  color: {
    type: String,
    required: true,
    validator: (value) => ['blue', 'gray', 'yellow', 'green'].includes(value),
  },
})

const iconBgClass = computed(() => {
  const classes = {
    blue: 'bg-blue-100',
    gray: 'bg-gray-100',
    yellow: 'bg-yellow-100',
    green: 'bg-green-100',
  }
  return classes[props.color]
})

const iconColorClass = computed(() => {
  const classes = {
    blue: 'text-blue-600',
    gray: 'text-gray-600',
    yellow: 'text-yellow-600',
    green: 'text-green-600',
  }
  return classes[props.color]
})
</script>
