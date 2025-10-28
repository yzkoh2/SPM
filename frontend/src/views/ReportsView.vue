<template>
    <div class="min-h-screen bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Reports</h1>
          <p class="text-sm text-gray-600 mt-1">Generate and view your task performance reports</p>
        </div>
  
        <!-- Tab Navigation -->
        <div class="bg-white rounded-lg shadow-md mb-6">
          <div class="border-b border-gray-200">
            <nav class="flex -mb-px" aria-label="Tabs">
              <router-link
                to="/reports/generate"
                :class="[
                  'whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm transition-colors',
                  isActiveTab('generate')
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  Generate Report
                </div>
              </router-link>
  
              <router-link
                to="/reports/history"
                :class="[
                  'whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm transition-colors',
                  isActiveTab('history')
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                <div class="flex items-center">
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  Past Reports
                </div>
              </router-link>
            </nav>
          </div>
        </div>
  
        <!-- Router View for nested routes -->
        <router-view></router-view>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useRoute } from 'vue-router'
  
  const route = useRoute()
  
  const isActiveTab = (tab) => {
    return route.path.includes(`/reports/${tab}`)
  }
  </script>