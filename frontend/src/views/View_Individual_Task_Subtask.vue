<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center py-6">
<router-link :to="backLink"
  class="flex items-center text-indigo-600 hover:text-indigo-500 mr-6 text-sm font-medium">
  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
  </svg>
  {{ backLinkText }}
</router-link>
          <div class="flex-1">
            <h1 class="text-2xl font-bold text-gray-900">{{ isSubtask ? 'Subtask Details' : 'Task Details' }}</h1>
          </div>
        </div>
      </div>
    </header>

    <StatusUpdateModal v-if="task && showStatusModal" :show="showStatusModal" :task="task"
      @close="showStatusModal = false" @update-status="handleStatusUpdate" />

    <div v-if="showEditForm"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-start justify-center">
      <div class="relative w-full max-w-2xl">
        <TaskForm :task-to-edit="taskToEdit" :all-users="allUsers" :is-subtask="isSubtask" :is-submitting="isUpdating"
        :current-collaborators="collaboratorDetails"
        :parent-deadline="parentTask ? parentTask.deadline : null" 
        submit-button-text="Update Task"
        submit-button-loading-text="Updating..." 
        @submit="updateTask" @cancel="closeEditModal" />
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-6">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-red-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error Loading Task</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
        <div class="mt-4">
          <button @click="fetchTaskDetails"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm cursor-pointer">
            Try Again
          </button>
        </div>
      </div>

      <div v-if="isSubtask && parentTask" class="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-900">Part of:</p>
            <h3 class="text-lg font-semibold text-blue-800">{{ parentTask.title }}</h3>
          </div>
          <router-link :to="`/tasks/${parentTaskId}`" class="text-blue-600 hover:text-blue-500 text-sm font-medium">
            View Parent Task →
          </router-link>
        </div>
      </div>

      <div v-if="task" class="space-y-6">
        <div class="bg-white rounded-lg shadow-md p-6 border-l-4" :class="getStatusBorderColor(task.status)">
          <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
              <h2 class="text-3xl font-bold text-gray-900 mb-2">{{ task.title }}</h2>
              <div class="flex items-center space-x-3">
                <div class="flex items-center space-x-2">
  <span
    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
    :class="getStatusBadgeColor(task.status)"
  >
    {{ task.status }}
  </span>
  
  <div 
    class="inline-flex items-center px-3 py-1.5 rounded-md font-bold text-sm"
    :class="getPriorityColorClass(task.priority)"
  >
    <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
    </svg>
    Priority {{ task.priority || 'N/A' }}
  </div>
</div>

                

                <RecurringIcon 
                  :is-recurring="task.is_recurring"
                  :recurrence-interval="task.recurrence_interval"
                  :recurrence-days="task.recurrence_days"
                />

                <span v-if="canEditTask" class="text-xs text-gray-500 flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  You can edit this task
                </span>
              </div>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button v-if="isCollaborator" @click="showStatusModal = true"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center cursor-pointer">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                  </path>
                </svg>
                Update Status
              </button>
              <button v-if="canEditTask" @click="editTask"
                class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium cursor-pointer">
                {{ isSubtask ? 'Edit Subtask' : 'Edit Task' }}
              </button>
              <button v-if="isOwner" @click="deleteTask"
                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium cursor-pointer">
                Delete
              </button>
            </div>
          </div>

          <div class="mt-4">
            <h3 class="text-lg font-medium text-gray-900 mb-2">Description</h3>
            <p class="text-gray-700 leading-relaxed">
              {{ task.description || 'No description provided' }}
            </p>
          </div>

          <div class="mt-6 grid grid-cols-1 md:grid-cols-4 gap-6 pt-6 border-t border-gray-200">

  <div>
    <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Priority</h4>
    <div class="mt-1">
      <div 
        class="inline-flex items-center px-3 py-1.5 rounded-md font-bold text-lg"
        :class="getPriorityColorClass(task.priority)"
      >
        {{ task.priority || 'N/A' }}
      </div>
    </div>
  </div>
  
  
  <div>
    <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Deadline</h4>
    <p class="mt-1 text-lg" :class="getDeadlineColor(task.deadline)">
      {{ formatDeadline(task.deadline) }}
    </p>
  </div>
  <div>
    <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Owner</h4>
    <p class="mt-1 text-lg text-gray-900"> {{ ownerDetails.name }} ID: {{ task.owner_id }}</p>
  </div>
  <div v-if="!isSubtask">
    <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Progress</h4>
    <div class="mt-1 flex items-center">
      <div class="flex-1 bg-gray-200 rounded-full h-2 mr-2">
        <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: getTaskProgress() + '%' }"></div>
      </div>
      <span class="text-sm text-gray-600">{{ getTaskProgress() }}%</span>
    </div>
  </div>
</div>

          <div v-if="collaboratorDetails.length > 0" class="mt-6 pt-6 border-t border-gray-200">
            <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">Collaborators</h4>
            <div class="flex flex-wrap gap-2">
              <div v-for="collab in collaboratorDetails" :key="collab.user_id"
                class="inline-flex items-center px-3 py-2 rounded-full text-sm bg-indigo-50 text-indigo-700">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                {{ collab.name }}
              </div>
            </div>
          </div>

          <!-- Recurring Task Details Section -->
          <div v-if="task.is_recurring" class="mt-6 pt-6 border-t border-gray-200">
            <div class="flex items-center mb-4">
              <svg class="w-5 h-5 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15">
                </path>
              </svg>
              <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Recurring Task Information</h4>
            </div>
            
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Recurrence Interval -->
                <div>
                  <p class="text-xs font-medium text-purple-700 mb-1">Recurrence Pattern</p>
                  <div class="flex items-center">
                    <svg class="w-4 h-4 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z">
                      </path>
                    </svg>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ formatRecurrenceInterval(task.recurrence_interval, task.recurrence_days) }}
                    </p>
                  </div>
                </div>

                <!-- Next Instance Date -->
                <div>
                  <p class="text-xs font-medium text-purple-700 mb-1">Next Scheduled Instance</p>
                  <div class="flex items-center">
                    <svg class="w-4 h-4 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M13 7l5 5m0 0l-5 5m5-5H6">
                      </path>
                    </svg>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ calculateNextInstanceDate(task.deadline, task.recurrence_interval, task.recurrence_days) }}
                    </p>
                  </div>
                </div>

                <!-- Recurrence End Date -->
                <div>
                  <p class="text-xs font-medium text-purple-700 mb-1">Recurrence Ends</p>
                  <div class="flex items-center">
                    <svg class="w-4 h-4 text-purple-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z">
                      </path>
                    </svg>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ formatRecurrenceEndDate(task.recurrence_end_date) }}
                    </p>
                  </div>
                </div>

                <!-- Status Badge -->
                <div>
                  <p class="text-xs font-medium text-purple-700 mb-1">Task Type</p>
                  <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-600 text-white">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z">
                      </path>
                    </svg>
                    Active Recurring Task
                  </div>
                </div>
              </div>

              <!-- Additional Info -->
              <div class="mt-3 pt-3 border-t border-purple-200">
                <p class="text-xs text-purple-800">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z">
                    </path>
                  </svg>
                  This task will automatically create a new instance when completed.
                </p>
              </div>
            </div>
          </div>

        </div>

        <div class="grid grid-cols-1 gap-6" :class="isSubtask ? 'md:grid-cols-2' : 'md:grid-cols-3'">
          <div v-if="!isSubtask" class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2">
                  </path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Subtasks</p>
                <p class="text-2xl font-semibold text-gray-900">{{ task.subtasks?.length || 0 }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
                  </path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Comments</p>
                <p class="text-2xl font-semibold text-gray-900">{{ totalCommentCount }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center">
              <div class="p-2 bg-purple-100 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13">
                  </path>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-600">Attachments</p>
                <p class="text-2xl font-semibold text-gray-900">{{ task.attachments?.length || 0 }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!isSubtask" class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900">Subtasks ({{ task.subtasks?.length || 0 }})</h3>
            <router-link :to="`/tasks/${task.id}/subtasks`"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium">
              View All Subtasks
            </router-link>
          </div>

          <div v-if="task.subtasks && task.subtasks.length > 0" class="space-y-3">
            <div v-for="subtask in task.subtasks.slice(0, 5)" :key="subtask.id"
  class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
  @click="$router.push(`/tasks/${task.id}/subtasks/${subtask.id}`)">
  <div class="flex items-center space-x-3">
    <div class="w-2 h-2 rounded-full" :class="getSubtaskStatusColor(subtask.status)"></div>
    <span class="text-gray-900">{{ subtask.title }}</span>
  </div>
  <div class="flex items-center space-x-2">
    <!-- Priority Badge for Subtask -->
    <div 
      class="inline-flex items-center px-2 py-0.5 rounded-md font-bold text-xs"
      :class="getPriorityColorClass(subtask.priority)"
    >
      Priority: {{ subtask.priority || 'N/A' }}
    </div>
    
    <RecurringIcon 
      :is-recurring="subtask.is_recurring"
      :recurrence-interval="subtask.recurrence_interval"
      :recurrence-days="subtask.recurrence_days"
    />
    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
      :class="getStatusBadgeColor(subtask.status)">
      {{ subtask.status }}
    </span>
  </div>
</div>
            <div v-if="task.subtasks.length > 5" class="text-center pt-4">
              <router-link :to="`/tasks/${task.id}/subtasks`"
                class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                View {{ task.subtasks.length - 5 }} more subtasks →
              </router-link>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2">
              </path>
            </svg>
            <p>No subtasks yet</p>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-6">
            Comments ({{ totalCommentCount }})
          </h3>

          <div class="mb-6 border-b border-gray-200 pb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Add a Comment</label>

            <Mentionable :keys="['@']"
              :items="collaboratorDetails.map(c => ({ value: c.username, label: c.name, user_id: c.user_id, role: c.role }))"
              offset="6" insert-space>
              <textarea v-model="newComment" rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Write a comment... Use @ to mention collaborators" @keydown.meta.enter="addComment"
                @keydown.ctrl.enter="addComment"></textarea>

              <template #item-@="{ item, isSelected }">
                <div
                  :class="['flex items-center p-2 space-x-3 cursor-pointer rounded-md transition-colors duration-150 ease-in-out', isSelected ? 'bg-indigo-100' : 'hover:bg-gray-50']">
                  <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                  <div class="flex-1">
                    <div class="font-medium text-gray-800">{{ item.label }}</div>
                    <div class="text-sm text-gray-500">{{ item.role }}</div>
                  </div>
                </div>
              </template>

              <template #no-result>
                <div class="text-gray-400 p-2">No users found</div>
              </template>
            </Mentionable>

            <div v-if="isCollaborator" class="mt-2 flex justify-end">
              <button @click="addComment({ body: newComment })" :disabled="!newComment.trim() || addingComment"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer">
                <span v-if="addingComment">Adding...</span>
                <span v-else>Add Comment</span>
              </button>
            </div>
          </div>

          <div v-if="topLevelComments.length > 0" class="space-y-6">
            <CommentItem v-for="comment in topLevelComments" :key="comment.id" :comment="comment"
              :current-user-id="authStore.user?.id" :collaborator-details="collaboratorDetails" @reply="addComment"
              @delete="handleDeleteComment" />
          </div>

          <div v-else v-if="isCollaborator" class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
              </path>
            </svg>
            <p>No comments yet. Be the first to comment!</p>
          </div>
        </div>

        <AttachmentModal :show="showAttachmentModal" :task-id="task.id" :is-uploading="isUploadingAttachment"
          @close="showAttachmentModal = false" @upload="addAttachment" v-if="task" />
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-xl font-semibold text-gray-900">
              Attachments ({{ task.attachments?.length || 0 }})
            </h3>

            <button v-if="isOwner" @click="showAttachmentModal = true"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 cursor-pointer">
              <span>Add Attachment</span>
            </button>
          </div>

          <div v-if="task.attachments && task.attachments.length > 0" class="space-y-3">
            <div v-for="attachment in task.attachments" :key="attachment.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div class="flex items-center space-x-3">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13">
                  </path>
                </svg>
                <span class="text-gray-900">{{ attachment.filename }}</span>
              </div>

              <div class="flex items-center space-x-2 ml-4">
                <a :href="attachment.url" target="_blank"
                  class="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                  View Attachment
                </a>
                <button v-if="isOwner" @click="deleteAttachment(task.id, attachment.id)"
                  class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium cursor-pointer">
                  Delete
                </button>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-8 text-gray-500">
            <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.172 7l6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13">
              </path>
            </svg>
            <p>No attachments</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Mentionable } from 'vue-mention'
import 'floating-vue/dist/style.css'
import StatusUpdateModal from '@/components/StatusUpdateModal.vue'
import CommentItem from '@/components/CommentItem.vue'
import TaskForm from '@/components/TaskForm.vue'
import AttachmentModal from '@/components/AttachmentModal.vue'
import RecurringIcon from '@/components/RecurringIcon.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isSubtask = computed(() => !!route.params.subtaskId)
const taskId = ref(null)
const parentTaskId = ref(null)

if (isSubtask.value) {
  parentTaskId.value = route.params.id
  taskId.value = route.params.subtaskId
} else {
  taskId.value = route.params.id
}

// Reactive data
const task = ref(null)
const parentTask = ref(null)
const comments = ref([])
const loading = ref(true)
const error = ref(null)
const showStatusModal = ref(false)
const newComment = ref('')
const addingComment = ref(false)
const collaborators = ref([])
const collaboratorDetails = ref([])
const allUsers = ref([])
const ownerDetails = ref(null)


// Modal States
const showAttachmentModal = ref(false)
const isUploadingAttachment = ref(false)

// Form states
const showEditForm = ref(false)
const isUpdating = ref(false)
const taskToEdit = ref(null)

// API configuration
const KONG_API_URL = "http://localhost:8000"

// Computed properties
const canEditTask = computed(() => {
  if (!task.value || !authStore.user) return false
  return task.value.owner_id === authStore.user.id
})

const isOwner = computed(() => {
  return authStore.user.id === task.value.owner_id
})

const isCollaborator = computed(() => {
  // Ensure we have the necessary data before checking
  if (!authStore.user || !task.value) {
    return false
  }

  // Check if the current user is the owner of the task
  const isOwner = authStore.user.id === task.value.owner_id

  // Check if the current user is in the collaborators list
  const isInCollaboratorsList = collaboratorDetails.value.some(
    (collaborator) => collaborator.user_id === authStore.user.id
  )

  // The user is considered a collaborator if they are the owner OR in the list
  return isOwner || isInCollaboratorsList
})


// Filter to show only top-level comments (no parent)
const topLevelComments = computed(() => {
  return comments.value.filter(comment => !comment.parent_comment_id)
})

// Calculate total comment count including all replies
const totalCommentCount = computed(() => {
  const countComments = (commentsList) => {
    return commentsList.reduce((total, comment) => {
      return total + 1 + (comment.replies ? countComments(comment.replies) : 0)
    }, 0)
  }
  return countComments(comments.value)
})

// Fetch task details from API
const fetchTaskDetails = async () => {
  try {
    loading.value = true
    error.value = null

    const response = await fetch(`${KONG_API_URL}/tasks/${taskId.value}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      task.value = await response.json()
      if (task.value?.owner_id) {
        ownerDetails.value = await fetchUserDetails(task.value.owner_id)
      }

      comments.value = task.value.comments || []
      if (task.value.attachments) {
        const urlPromises = task.value.attachments.map(async (attachment) => {
          const url = await getS3URL(task.value.id, attachment.id)
          return { ...attachment, url: url }
        })
        // Wait for all URLs to be fetched and update the attachments array
        task.value.attachments = await Promise.all(urlPromises)
      }
    } else if (response.status === 404) {
      error.value = 'Task not found'
    } else {
      error.value = `Failed to load task: ${response.status}`
    }

    // Fetch parent task details
    if (isSubtask.value && parentTaskId.value) {
      const parentResponse = await fetch(`${KONG_API_URL}/tasks/${parentTaskId.value}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (parentResponse.ok) {
        parentTask.value = await parentResponse.json()
      } else {
        console.warn('Failed to load parent task details')
      }
    }

    // Fetch collaborator details
    await fetchCollaborators(taskId.value)

  } catch (err) {
    console.error('Error fetching task details:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

const fetchCollaborators = async (taskId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/collaborators`)

    if (response.ok) {
      collaborators.value = await response.json()

      // Fetch details for each collaborator
      const detailsPromises = collaborators.value.map(collab =>
        fetchUserDetails(collab.user_id)
      )

      const details = await Promise.all(detailsPromises)

      // Combine collaborator info with user details
      collaboratorDetails.value = collaborators.value.map((collab, index) => ({
        user_id: collab.user_id,
        name: details[index]?.name || `User ${collab.user_id}`,
        role: details[index]?.role || 'Unknown',
        username: details[index]?.username
      }))
    } else {
      console.warn('Failed to load collaborators')
      collaboratorDetails.value = []
    }
  } catch (err) {
    console.error('Error fetching collaborators:', err)
    collaboratorDetails.value = []
  }
}

const fetchAllUsers = async () => {
  try {
    // Assume you have an endpoint that returns all users
    const response = await fetch(`${KONG_API_URL}/user`);
    if (response.ok) {
      allUsers.value = await response.json();
    } else {
      console.error("Failed to fetch all users.");
    }
  } catch (err) {
    console.error("Error fetching all users:", err);
  }
};

const fetchUserDetails = async (userId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/user/${userId}`)

    if (response.ok) {
      return await response.json()
    } else {
      console.warn(`Failed to load user details for ID ${userId}`)
      return null
    }
  } catch (err) {
    console.error(`Error fetching user ${userId}:`, err)
    return null
  }
}

const getS3URL = async (taskId, attachmentId) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/attachments/${attachmentId}`)

    if (response.ok) {
      const data = await response.json()
      return data.url
    } else {
      console.warn(`Failed to get S3 URL for attachment ${attachmentId}`)
      return '#'
    }
  } catch (err) {
    console.error('Error fetching S3 URL:', err)
    return '#'
  }
}

const addAttachment = async ({ file, name, taskId }) => {
  isUploadingAttachment.value = true
  const formData = new FormData()
  formData.append('file', file)
  formData.append('filename', name)

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/attachments`, {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      // Refresh task details to get updated attachments
      await fetchTaskDetails()
      alert('Attachment uploaded successfully!')
      showAttachmentModal.value = false
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to upload attachment')
    }
  } catch (err) {
    console.error('Error uploading attachment:', err)
    alert('Failed to upload attachment: ' + err.message)
  } finally {
    isUploadingAttachment.value = false
  }
}

const deleteAttachment = async (taskId, attachmentId) => {
  if (!confirm('Are you sure you want to delete this attachment?')) {
    return
  }

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/attachments/${attachmentId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      // Refresh task details to get updated attachments
      await fetchTaskDetails()
      alert('Attachment deleted successfully!')
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to delete attachment')
    }
  } catch (err) {
    console.error('Error deleting attachment:', err)
    alert('Failed to delete attachment: ' + err.message)
  }
}

// Handle status update
const handleStatusUpdate = async ({ newStatus, comment }) => {
  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: authStore.user.id,
        status: newStatus
      })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to update status')
    }

    // Update local task data
    if (data.task) {
      task.value.status = data.task.status
    }

    // Refresh task details to get updated data
    await fetchTaskDetails()

    // Close modal
    showStatusModal.value = false

    // Show success message
    alert('Task status updated successfully!')
  } catch (err) {
    console.error('Error updating status:', err)
    alert('Failed to update status: ' + err.message)
    showStatusModal.value = false
    throw err
  }
}

// Add comment (top-level)
const addComment = async ({ body, parentCommentId = null }) => {
  if (!body.trim()) return

  try {
    addingComment.value = true

    const mentionRegex = /@(\w+)/g;
    const matches = [...body.matchAll(mentionRegex)];
    const mentionedUsernames = matches.map(match => match[1]);
    const uniqueUsernames = [...new Set(mentionedUsernames)];
    const mention_ids = uniqueUsernames.map(username => {
      const collaborator = collaboratorDetails.value.find(c => c.username === username);
      return collaborator ? collaborator.user_id : null;
    }).filter(id => id !== null);

    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        body: body,
        author_id: authStore.user.id,
        parent_comment_id: parentCommentId,
        mention_ids: mention_ids
      })
    })

    if (response.ok) {
      // Refresh task details to get updated comments with nested structure
      await fetchTaskDetails()
      if (!parentCommentId) {
        newComment.value = ''
      }
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add comment')
    }
  } catch (err) {
    console.error('Error adding comment:', err)
    alert('Failed to add comment: ' + err.message)
  } finally {
    addingComment.value = false
  }
}

// Handle delete comment
const handleDeleteComment = async (commentId) => {
  if (!confirm('Are you sure you want to delete this comment?')) {
    return
  }

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/deletecomment/${commentId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      // Refresh task details to get updated comments
      await fetchTaskDetails()
    } else {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to delete comment')
    }
  } catch (err) {
    console.error('Error deleting comment:', err)
    alert('Failed to delete comment: ' + err.message)
  }
}

// Action methods
const editTask = () => {
  taskToEdit.value = { ...task.value };
  showEditForm.value = true;
};

const closeEditModal = () => {
  showEditForm.value = false;
  taskToEdit.value = null;
};

const updateTask = async (formData) => {
  isUpdating.value = true
  try {
    const originalTask = taskToEdit.value;
    const changedFields = {};

    for (const key in formData) {
      if (key === 'id') continue;

      let originalValue = originalTask[key];
      let currentValue = formData[key];

      if (key === 'deadline' || key === 'recurrence_end_date') {
        originalValue = originalValue ? new Date(originalValue).toISOString().slice(0, 16) : null;
        currentValue = currentValue || null;
      }

      if (originalValue !== currentValue) {
        changedFields[key] = currentValue;
      }
    }

    if (Object.keys(changedFields).length === 0) {
      closeEditModal();
      return; // No changes to update
    }

    const payload = {
      ...changedFields,
      user_id: authStore.user.id
    };

    const response = await fetch(`${KONG_API_URL}/tasks/${formData.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update task');
    }

    await fetchTaskDetails();
    closeEditModal();
  } catch (err) {
    console.error('Error updating task:', err);
    alert('Failed to update task: ' + err.message);
  } finally {
    isUpdating.value = false;
  }
};

const deleteTask = async () => {
  if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
    return
  }

  try {
    const response = await fetch(`${KONG_API_URL}/tasks/${task.value.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: authStore.user.id
      })
    })

    const data = await response.json()

    if (response.ok) {
      alert(data.message || 'Task deleted successfully')
      if (isSubtask.value) {
        router.push(`/tasks/${parentTaskId.value}/subtasks`)
      } else {
        router.push('/')
      }
    } else {
      throw new Error(data.error || `Failed to delete: ${response.status}`)
    }
  } catch (err) {
    console.error('Error deleting task:', err)
    alert('Failed to delete task: ' + err.message)
  }
}

// Calculate task progress based on subtasks
const getTaskProgress = () => {
  if (!task.value.subtasks || task.value.subtasks.length === 0) {
    return task.value.status === 'Completed' ? 100 : 0
  }

  const completedCount = task.value.subtasks.filter(s => s.status === 'Completed').length
  return Math.round((completedCount / task.value.subtasks.length) * 100)
}

// Utility methods
const getStatusBorderColor = (status) => {
  const colors = {
    'Unassigned': 'border-gray-400',
    'Ongoing': 'border-yellow-400',
    'Under Review': 'border-orange-400',
    'Completed': 'border-green-400'
  }
  return colors[status] || 'border-gray-400'
}

const getStatusBadgeColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-100 text-gray-800',
    'Ongoing': 'bg-yellow-100 text-yellow-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    'Completed': 'bg-green-100 text-green-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getSubtaskStatusColor = (status) => {
  const colors = {
    'Unassigned': 'bg-gray-400',
    'Ongoing': 'bg-yellow-400',
    'Under Review': 'bg-orange-400',
    'Completed': 'bg-green-400'
  }
  return colors[status] || 'bg-gray-400'
}

const getDeadlineColor = (deadline) => {
  if (!deadline) return 'text-gray-600'

  const now = new Date()
  const deadlineDate = new Date(deadline)

  if (deadlineDate < now) return 'text-red-600 font-medium'
  if (deadlineDate.toDateString() === now.toDateString()) return 'text-orange-600 font-medium'
  return 'text-gray-900'
}

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline set'
  const date = new Date(deadline)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Recurring task helper functions
const formatRecurrenceInterval = (interval, days) => {
  if (interval === 'custom' && days) {
    return `Every ${days} day${days > 1 ? 's' : ''}`
  }
  
  const intervalMap = {
    'daily': 'Daily',
    'weekly': 'Weekly',
    'monthly': 'Monthly'
  }
  
  return intervalMap[interval] || 'Unknown'
}

const calculateNextInstanceDate = (deadline, interval, days) => {
  if (!deadline) return 'Not set'
  
  const currentDeadline = new Date(deadline)
  let nextDate = new Date(currentDeadline)
  
  if (interval === 'daily') {
    nextDate.setDate(nextDate.getDate() + 1)
  } else if (interval === 'weekly') {
    nextDate.setDate(nextDate.getDate() + 7)
  } else if (interval === 'monthly') {
    nextDate.setMonth(nextDate.getMonth() + 1)
  } else if (interval === 'custom' && days) {
    nextDate.setDate(nextDate.getDate() + days)
  }
  
  return nextDate.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatRecurrenceEndDate = (endDate) => {
  if (!endDate) return 'No end date'
  const date = new Date(endDate)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getPriorityColorClass = (priority) => {
  if (!priority) return 'bg-gray-100 text-gray-700 border border-gray-300';
  
  if (priority >= 8 && priority <= 10) {
    return 'bg-red-100 text-red-800 border border-red-300';
  } else if (priority >= 4 && priority <= 7) {
    return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
  } else if (priority >= 1 && priority <= 3) {
    return 'bg-green-100 text-green-800 border border-green-300';
  }
  return 'bg-gray-100 text-gray-700 border border-gray-300';
};

// Add these new computed properties
const backLink = computed(() => {
  if (isSubtask.value) { //
    return `/tasks/${parentTaskId.value}/subtasks` //
  }
  // Check if we came from a project
  if (route.query.fromProject) {
    return `/projects/${route.query.fromProject}`
  }
  // Fallback to the default personal taskboard
  return '/' //
})

const backLinkText = computed(() => {
  if (isSubtask.value) {
    return 'Back to Subtasks' //
  }
  if (route.query.fromProject) {
    return 'Back to Project'
  }
  return 'Back to Tasks' //
})

watch(
  () => [route.params.id, route.params.subtaskId],
  ([newTaskId, newSubtaskId]) => {
    if (isSubtask.value) {
      parentTaskId.value = newTaskId
      taskId.value = newSubtaskId
    } else {
      taskId.value = newTaskId
    }
    fetchTaskDetails()
  }
)

// Load task details when component mounts
onMounted(() => {
  fetchTaskDetails()
  fetchAllUsers();
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>