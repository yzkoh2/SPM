import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Login from '@/views/Login.vue'
import PersonalTaskboard from '@/views/PersonalTaskboard.vue'
import ScheduleView from '@/views/ScheduleView.vue'
import PersonalSchedule from '@/views/PersonalSchedule.vue'
import TeamSchedule from '@/views/TeamSchedule.vue'
import ProjectSchedule from '@/views/ProjectSchedule.vue'
import DepartmentSchedule from '@/views/DepartmentSchedule.vue'
import CompanySchedule from '@/views/CompanySchedule.vue'

// RBAC Helper function
const hasAccess = (userRole, allowedRoles) => {
  if (!userRole) return false
  return allowedRoles.includes(userRole.toUpperCase())
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: PersonalTaskboard,
      meta: { requiresAuth: true },
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
          meta: { 
            requiresAuth: true,
            // Personal schedule is available to all authenticated users
          },
        },
        {
          path: 'team',
          name: 'schedule-team',
          component: TeamSchedule,
          meta: { 
            requiresAuth: true,
            allowedRoles: ['STAFF', 'MANAGER', 'DIRECTOR', 'HR', 'SM']
          },
        },
        {
          path: 'project',
          name: 'schedule-project',
          component: ProjectSchedule,
          meta: { 
            requiresAuth: true,
            allowedRoles: ['STAFF', 'MANAGER', 'DIRECTOR', 'HR', 'SM']
          },
        },
        {
          path: 'department',
          name: 'schedule-department',
          component: DepartmentSchedule,
          meta: { 
            requiresAuth: true,
            allowedRoles: ['DIRECTOR', 'HR', 'SM']
          },
        },
        {
          path: 'company',
          name: 'schedule-company',
          component: CompanySchedule,
          meta: { 
            requiresAuth: true,
            allowedRoles: ['HR', 'SM']
          },
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectTaskboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/projects/:id',
      name: 'project-dashboard',
      component: () => import('@/views/ProjectDashboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks/:id',
      name: 'task-details',
      component: () => import('@/views/View_Individual_Task_Subtask.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks/:id/subtasks',
      name: 'task-subtasks',
      component: () => import('@/views/View_SubTasks.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks/:id/subtasks/:subtaskId',
      name: 'task-subtasks-details',
      component: () => import('@/views/View_Individual_Task_Subtask.vue'),
      meta: { requiresAuth: true },
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
      },
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
      },
    },

    {
      path: '/taskboard/team',
      name: 'team-taskboard',
      component: () => import('@/views/TeamTaskboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/taskboard/department',
      name: 'department-taskboard',
      component: () => import('@/views/DepartmentTaskboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/reports',
      component: () => import('@/views/ReportsView.vue'),
      meta: { requiresAuth: true },
      redirect: '/reports/generate',
      children: [
        {
          path: 'generate',
          name: 'reports-generate',
          component: () => import('@/views/ReportGeneration.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'history',
          name: 'reports-history',
          component: () => import('@/views/PastReports.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
  ],
})

// Navigation Guard with JWT Token Verification and RBAC
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('authToken')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  // If route requires authentication but no token exists
  if (requiresAuth && !token) {
    return next({ name: 'login' })
  }

  // If token exists, verify it with the backend
  if (token) {
    try {
      const response = await fetch('http://localhost:8000/user/verifyJWT', {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!response.ok) {
        throw new Error('Token verification failed')
      }

      // RBAC: Check if user has required role for this route
      const allowedRoles = to.meta.allowedRoles
      if (allowedRoles && allowedRoles.length > 0) {
        const userRole = authStore.user?.role
        if (!hasAccess(userRole, allowedRoles)) {
          alert(`Access denied. This page requires one of the following roles: ${allowedRoles.join(', ')}`)
          // Redirect to personal schedule (available to all)
          return next({ name: 'schedule-personal' })
        }
      }

      // If trying to access login page while authenticated, redirect to dashboard
      if (to.name === 'login') {
        return next({ name: 'dashboard' })
      }

      // Token is valid and user has access, proceed to route
      return next()
    } catch (error) {
      console.error('Auth check failed:', error)

      // Clear auth store state AND localStorage
      authStore.user = null
      authStore.token = null
      localStorage.removeItem('authToken')
      localStorage.removeItem('userID')
      localStorage.removeItem('user')

      // If route requires auth, redirect to login
      if (requiresAuth) {
        return next({ name: 'login' })
      }

      // For public routes, allow access without token
      return next()
    }
  }

  // No token and route doesn't require auth - continue
  next()
})

export default router