import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import PersonalTaskboard from '@/views/PersonalTaskboard.vue'
import ScheduleView from '@/views/ScheduleView.vue'
import PersonalSchedule from '@/views/PersonalSchedule.vue'
import TeamSchedule from '@/views/TeamSchedule.vue'
import ProjectSchedule from '@/views/ProjectSchedule.vue'
import DepartmentSchedule from '@/views/DepartmentSchedule.vue'

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
      path: '/schedule',
      component: ScheduleView,
      meta: { requiresAuth: true },
      redirect: '/schedule/personal',
      children: [
        {
          path: 'personal',
          name: 'schedule-personal',
          component: PersonalSchedule,
          meta: { requiresAuth: true }
        },
        {
          path: 'team',
          name: 'schedule-team',
          component: TeamSchedule,
          meta: { requiresAuth: true }
        },
        {
          path: 'project',
          name: 'schedule-project',
          component: ProjectSchedule,
          meta: { requiresAuth: true }
        },
        {
          path: 'department',
          name: 'schedule-department',
          component: DepartmentSchedule,
          meta: { requiresAuth: true }
        }
      ]
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
          console.error('Error checking subtask ownership:', error)
          next(`/tasks/${to.params.id}/subtasks`)
        }
      }
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('userID')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.name === 'login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router