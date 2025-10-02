<script setup>
  import { RouterView } from 'vue-router';
  import { useAuthStore } from '@/stores/auth'
  import Navbar from '@/components/Navbar.vue'

  const authStore = useAuthStore();
</script>

<template>
  <Navbar v-if="authStore.isAuthenticated" />
  <RouterView />
</template>

<style scoped></style>
