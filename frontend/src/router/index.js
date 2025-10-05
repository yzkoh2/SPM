import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard,
      // Add meta field to mark this as a protected route
      meta: { requiresAuth: true } 
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/tasks/:id',
      name: 'task-details',
      component: () => import('@/views/View_Individual_Task_Subtask.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks/:id/subtasks',
      name: 'task-subtasks',
      component: () => import('@/views/View_SubTasks.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks/:id/subtasks/:subtaskId',
      name: 'task-subtasks-details',
      component: () => import('@/views/View_Individual_Task_Subtask.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectTaskboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks/:id/edit',
      name: 'task-edit',
      component: () => import('@/views/Edit_Task_Subtask.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks/:id/subtasks/:subtaskId/edit',
      name: 'subtask-edit', 
      component: () => import('@/views/Edit_Task_Subtask.vue'),
      meta: { requiresAuth: true }
    }    
    
  ],
})

// Nav Guard for JWT Token
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('authToken');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !token) {
    // If the route requires auth and there's no token, redirect to login.
    return next({ name: 'login' });
  }

  if (token) {
    try {
      // If a token exists, verify it with the backend.
      const response = await fetch('http://localhost:8000/user/verifyJWT', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        // If the token is invalid (expired, tampered), throw an error.
        throw new Error('Token verification failed');
      }
      
      // Token is valid.
      // If the user is trying to access the login page, redirect them to the dashboard.
      if (to.name === 'login') {
        return next({ name: 'dashboard' });
      }

    } catch (error) {
      // If verification fails, the token is bad.
      console.error('Auth check failed:', error);
      // Remove the invalid token from storage.
      // localStorage.removeItem('authToken');
      
      // If the route they were trying to access requires auth, redirect to login.
      if (requiresAuth) {
        return next({ name: 'login' });
      }
    }
  }

  // For all other cases (e.g., public routes), allow navigation.
  return next();
});

export default router
