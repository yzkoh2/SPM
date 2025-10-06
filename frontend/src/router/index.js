import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import PersonalTaskboard from '@/views/PersonalTaskboard.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: PersonalTaskboard,
      meta: { requiresAuth: true } 
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectTaskboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects/:id',
      name: 'project-dashboard',
      component: () => import('@/views/ProjectDashboard.vue'),
      meta: { requiresAuth: true }
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
      path: '/tasks/:id/edit',
      name: 'task-edit',
      component: () => import('@/views/Edit_Task_Subtask.vue'),
      meta: { requiresAuth: true },
      beforeEnter: async (to, from, next) => {
        const userId = parseInt(localStorage.getItem('userID'))
        
        try {
          const response = await fetch(`http://localhost:8000/tasks/${to.params.id}`)
          const task = await response.json()
          
          if (task.owner_id === userId) {
            next()
          } else {
            alert('You do not have permission to edit this task')
            next(`/tasks/${to.params.id}`)
          }
        } catch (error) {
          console.error('Error checking task ownership:', error)
          next('/tasks')
        }
      }
    },
    {
      path: '/tasks/:id/subtasks/:subtaskId/edit',
      name: 'subtask-edit', 
      component: () => import('@/views/Edit_Task_Subtask.vue'),
      meta: { requiresAuth: true },
      beforeEnter: async (to, from, next) => {
        const userId = parseInt(localStorage.getItem('userID'))
        
        try {
          const response = await fetch(`http://localhost:8000/tasks/${to.params.subtaskId}`)
          const task = await response.json()
          
          if (task.owner_id === userId) {
            next()
          } else {
            alert('You do not have permission to edit this subtask')
            next(`/tasks/${to.params.id}/subtasks/${to.params.subtaskId}`)
          }
        } catch (error) {
          console.error('Error checking task ownership:', error)
          next('/tasks')
        }
      }
    }    
  ],
})

// Nav Guard for JWT Token
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('authToken');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !token) {
    return next({ name: 'login' });
  }

  if (token) {
    try {
      const response = await fetch('http://localhost:8000/user/verifyJWT', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Token verification failed');
      }
      
      if (to.name === 'login') {
        return next({ name: 'dashboard' });
      }

    } catch (error) {
      console.error('Auth check failed:', error);
      
      if (requiresAuth) {
        return next({ name: 'login' });
      }
    }
  }

  return next();
});

export default router