<template>
    <div v-if="isRecurring" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
      <svg 
        class="w-3 h-3 mr-1" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>
      <span>{{ recurrenceText }}</span>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  
  const props = defineProps({
    isRecurring: {
      type: Boolean,
      default: false
    },
    recurrenceInterval: {
      type: String,
      default: null
    },
    recurrenceDays: {
      type: Number,
      default: null
    }
  })
  
  const recurrenceText = computed(() => {
    if (props.recurrenceInterval === 'custom' && props.recurrenceDays) {
      return `Recurring every ${props.recurrenceDays} day${props.recurrenceDays > 1 ? 's' : ''}`
    }
    
    const intervalMap = {
      'daily': 'Recurring Daily',
      'weekly': 'Recurring Weekly',
      'monthly': 'Recurring Monthly'
    }
    
    return intervalMap[props.recurrenceInterval] || 'Recurring'
  })
  </script>