<template>
  <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-8">
          <div class="flex-shrink-0">
            <h1 class="text-xl font-bold text-gray-900">Task Management System</h1>
          </div>

          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <router-link
                to="/"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="
                  (isActiveRoute('/') || isActiveRoute('/taskboard')) && !isActiveRoute('/projects') && !isActiveRoute('/schedule')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                "
              >
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    ></path>
                  </svg>
                  Tasks
                </div>
              </router-link>

              <router-link
                to="/projects"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="
                  isActiveRoute('/projects')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                "
              >
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                    ></path>
                  </svg>
                  Projects
                </div>
              </router-link>

              <router-link
                to="/schedule"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="
                  isActiveRoute('/schedule')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                "
              >
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    ></path>
                  </svg>
                  Schedule
                </div>
              </router-link>
              <router-link
                to="/reports"
                class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
                :class="
                  isActiveRoute('/reports')
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                "
              >
                <div class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16h6m2 4H7a2 2 0 01-2-2V6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v10a2 2 0 01-2 2z"
                    ></path>
                  </svg>
                  Generate Report
                </div>
              </router-link>
            </div>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-3">
            <div class="hidden sm:block text-right">
              <p class="text-sm font-medium text-gray-900">{{ authStore.user?.name || 'User' }}</p>
              <p class="text-xs text-gray-500 capitalize">{{ authStore.user?.role || 'staff' }}</p>
            </div>
            <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
              <svg
                class="w-5 h-5 text-indigo-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                ></path>
              </svg>
            </div>
          </div>

          <button
            @click="authStore.logout()"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            Logout
          </button>

          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                v-if="!mobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              ></path>
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 py-3">
        <div class="space-y-1">
          <router-link
            to="/"
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="
              isActiveRoute('/') && !isActiveRoute('/projects') && !isActiveRoute('/schedule')
                ? 'bg-indigo-100 text-indigo-700'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            "
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                ></path>
              </svg>
              Tasks
            </div>
          </router-link>

          <router-link
            to="/projects"
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="
              isActiveRoute('/projects')
                ? 'bg-indigo-100 text-indigo-700'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            "
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                ></path>
              </svg>
              Projects
            </div>
          </router-link>

          <router-link
            to="/schedule"
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="
              isActiveRoute('/schedule')
                ? 'bg-indigo-100 text-indigo-700'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            "
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                ></path>
              </svg>
              Schedule
            </div>
          </router-link>

          <router-link
            to="/reports"
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors"
            :class="
              isActiveRoute('/reports')
                ? 'bg-indigo-100 text-indigo-700'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            "
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16h6m2 4H7a2 2 0 01-2-2V6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v10a2 2 0 01-2 2z"
                ></path>
              </svg>
              Generate Report
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

const isActiveRoute = (routePath) => {
  return (
    router.currentRoute.value.path === routePath ||
    router.currentRoute.value.path.startsWith(routePath + '/')
  )
}
</script>
