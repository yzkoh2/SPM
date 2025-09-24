import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(JSON.parse(localStorage.getItem('user')))
  const token = ref(localStorage.getItem('authToken'))
  const router = useRouter()

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const currentUserId = computed(() => user.value?.id)

  // Actions
  function login(userData, authToken) {
    user.value = userData
    token.value = authToken
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('authToken', authToken)
    localStorage.setItem('userID', userData.id) // Continue setting this for compatibility
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('authToken')
    localStorage.removeItem('userID')
    router.push('/login')
  }

  function checkAuth() {
    if (!isAuthenticated.value) {
      logout()
    }
  }

  return { user, token, isAuthenticated, currentUserId, login, logout, checkAuth }
})