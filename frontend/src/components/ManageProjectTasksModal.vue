<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div
      class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
    >
      <div
        class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <div
        class="inline-block w-full max-w-3xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-2xl rounded-2xl relative z-10"
      >
        <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-5">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-2xl font-bold text-white">Manage Project Tasks</h3>
              <p class="text-indigo-100 text-sm mt-1">
                Create new tasks or add existing ones to this project
              </p>
            </div>
            <button
              @click="$emit('close')"
              class="text-indigo-100 hover:text-white transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                ></path>
              </svg>
            </button>
          </div>
        </div>

        <div class="p-6">
          <div v-if="error" class="mb-4 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
              <p class="text-sm text-red-700 font-medium">{{ error }}</p>
            </div>
          </div>

          <div
            v-if="successMessage"
            class="mb-4 p-4 bg-green-50 border-l-4 border-green-400 rounded-r-lg"
          >
            <div class="flex items-center">
              <svg class="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
              <p class="text-sm text-green-700 font-medium">{{ successMessage }}</p>
            </div>
          </div>

          <!-- Tab Headers -->
          <div class="border-b border-gray-200 mb-6">
            <nav class="-mb-px flex space-x-8">
              <button
                @click="activeTab = 'create'"
                :class="[
                  activeTab === 'create'
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-semibold text-sm transition-colors flex items-center',
                ]"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4v16m8-8H4"
                  ></path>
                </svg>
                Create New Task
              </button>
              <button
                @click="activeTab = 'add'"
                :class="[
                  activeTab === 'add'
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-semibold text-sm transition-colors flex items-center',
                ]"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  ></path>
                </svg>
                Add Existing Task
              </button>
              <button
                @click="activeTab = 'remove'"
                :class="[
                  activeTab === 'remove'
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-semibold text-sm transition-colors flex items-center',
                ]"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 4v16m8-8H4"
                  ></path>
                </svg>
                Remove Task from Project
              </button>
            </nav>
          </div>

          <div v-if="activeTab === 'create'" class="max-h-[60vh] overflow-y-auto pr-2">
            <form @submit.prevent="createTask" class="space-y-6">
              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  Task Title
                  <span class="text-red-500 ml-1">*</span>
                </label>
                <input
                  v-model="newTask.title"
                  type="text"
                  required
                  placeholder="Enter a clear, descriptive task title"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  Deadline
                  <span class="text-red-500 ml-1">*</span>
                </label>
                <input
                  v-model="newTask.deadline"
                  type="datetime-local"
                  :min="minDeadline"
                  :max="maxDeadline"
                  placeholder="dd/mm/yyyy, --:-- --"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
                <p
                  v-if="projectDeadline && newTask.deadline > formatDateForInput(projectDeadline)"
                  class="text-xs text-red-600 mt-1"
                >
                  ⚠️ The task deadline cannot be later than the project deadline.
                </p>
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  Description
                  <span class="text-red-500 ml-1">*</span>
                </label>
                <textarea
                  v-model="newTask.description"
                  rows="4"
                  placeholder="Describe the task in detail..."
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
                ></textarea>
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  Status
                </label>
                <select
                  v-model="newTask.status"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white"
                >
                  <option value="Unassigned">Unassigned</option>
                  <option value="Ongoing">Ongoing</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <div>
                <label class="flex items-center text-sm font-semibold text-gray-700 mb-2">
                  Priority
                </label>
                <div class="relative">
                  <input
                    v-model.number="newTask.priority"
                    type="range"
                    min="1"
                    max="10"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                  <div class="flex justify-between text-xs text-gray-500 mt-2 px-1">
                    <span>1</span>
                    <span>2</span>
                    <span>3</span>
                    <span>4</span>
                    <span>5</span>
                    <span>6</span>
                    <span>7</span>
                    <span>8</span>
                    <span>9</span>
                    <span>10</span>
                  </div>
                </div>
              </div>

              <div class="border-t border-gray-200 pt-6">
                <label class="flex items-center text-sm text-gray-700 cursor-pointer">
                  <input
                    v-model="newTask.is_recurring"
                    type="checkbox"
                    class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 cursor-pointer mr-2"
                  />
                  Is this a recurring task?
                </label>
              </div>

              <div
                v-if="newTask.is_recurring"
                class="space-y-6 bg-gray-50 p-5 rounded-lg border border-gray-200"
              >
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2"
                    >Recurrence Interval</label
                  >
                  <select
                    v-model="newTask.recurrence_interval"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>

                <div v-if="newTask.recurrence_interval === 'custom'">
                  <label class="block text-sm font-semibold text-gray-700 mb-2"
                    >Recurrence Days</label
                  >
                  <input
                    v-model.number="newTask.recurrence_days"
                    type="number"
                    min="1"
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    placeholder="Enter number of days (e.g., 3)"
                  />
                </div>

                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2"
                    >Recurrence End Date</label
                  >
                  <input
                    v-model="newTask.recurrence_end_date"
                    type="datetime-local"
                    :min="minRecurrenceEndDate"
                    :max="maxDeadline"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                  <p class="text-xs text-gray-500 mt-1">
                    Optional. If not set, the recurrance end date will be the project deadline.
                  </p>
                </div>
              </div>
              <div class="border-t border-gray-200 pt-6">
                <h3 class="text-base font-semibold text-gray-900 mb-1">Manage Collaborators</h3>
                <p class="text-sm text-gray-500 mb-4">
                  {{
                    collaboratorDetails.length === 0
                      ? 'No collaborators added yet.'
                      : `${collaboratorDetails.length} collaborator(s) added.`
                  }}
                </p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label class="text-xs text-gray-600 mb-1 block">Filter by Department</label>
                    <select
                      v-model="selectedDepartment"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white text-sm"
                    >
                      <option v-for="dept in availableDepartments" :key="dept" :value="dept">
                        {{ dept }}
                      </option>
                    </select>
                  </div>

                  <div>
                    <label class="text-xs text-gray-600 mb-1 block">Filter by Team</label>
                    <select
                      v-model="selectedTeam"
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white text-sm"
                    >
                      <option v-for="team in availableTeams" :key="team" :value="team">
                        {{ team }}
                      </option>
                    </select>
                  </div>
                </div>

                <div class="flex gap-3">
                  <select
                    v-model="selectedUser"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white text-sm"
                  >
                    <option value="">Select a user to add...</option>
                    <option v-for="user in filteredUsers" :key="user.id" :value="user.id">
                      {{ user.name }} ({{ user.role }})
                    </option>
                  </select>
                  <button
                    type="button"
                    @click="addCollaborator"
                    :disabled="!selectedUser"
                    class="px-5 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all whitespace-nowrap"
                  >
                    Add
                  </button>
                </div>

                <div v-if="collaboratorDetails.length > 0" class="flex flex-wrap gap-2 mt-4">
                  <div
                    v-for="collaborator in collaboratorDetails"
                    :key="collaborator.id"
                    class="flex items-center gap-2 px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full text-sm"
                  >
                    {{ collaborator.name }}
                    <button
                      type="button"
                      @click="removeCollaborator(collaborator.id)"
                      class="text-purple-700 hover:text-purple-900 font-bold"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
              <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  @click="$emit('close')"
                  class="px-6 py-3 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="creating"
                  class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg text-sm font-semibold hover:from-indigo-700 hover:to-indigo-800 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center"
                >
                  <svg
                    v-if="!creating"
                    class="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 4v16m8-8H4"
                    ></path>
                  </svg>
                  <svg v-else class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  {{ creating ? 'Creating...' : 'Create Task' }}
                </button>
              </div>
            </form>
          </div>

          <div v-if="activeTab === 'add'">
            <div class="space-y-4">
              <div v-if="loadingStandaloneTasks" class="text-center py-12">
                <div
                  class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"
                ></div>
                <p class="text-sm text-gray-500 mt-4">Loading your tasks...</p>
              </div>

              <div
                v-else-if="standaloneTasks.length > 0"
                class="space-y-3 max-h-96 overflow-y-auto pr-2"
              >
                <div
                  v-for="task in standaloneTasks"
                  :key="task.id"
                  class="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-xl p-5 hover:border-indigo-400 hover:shadow-md transition-all"
                >
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      <h4 class="font-semibold text-gray-900 text-lg">{{ task.title }}</h4>
                      <p v-if="task.description" class="text-sm text-gray-600 mt-2 line-clamp-2">
                        {{ task.description }}
                      </p>
                      <div class="flex items-center space-x-4 mt-3">
                        <span
                          :class="[
                            'px-3 py-1 rounded-full text-xs font-semibold',
                            getStatusColor(task.status),
                          ]"
                        >
                          {{ task.status }}
                        </span>
                        <span v-if="task.deadline" class="text-xs text-gray-500 flex items-center">
                          <svg
                            class="w-4 h-4 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                            ></path>
                          </svg>
                          {{ formatDate(task.deadline) }}
                        </span>
                      </div>
                    </div>
                    <button
                      @click="addTaskToProject(task.id)"
                      :disabled="addingTask === task.id"
                      class="ml-4 px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white text-sm font-semibold rounded-lg hover:from-indigo-700 hover:to-indigo-800 disabled:from-gray-400 disabled:to-gray-400 transition-all shadow-md hover:shadow-lg flex items-center whitespace-nowrap"
                    >
                      <svg
                        v-if="!addingTask"
                        class="w-4 h-4 mr-1"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 4v16m8-8H4"
                        ></path>
                      </svg>
                      {{ addingTask === task.id ? 'Adding...' : 'Add to Project' }}
                    </button>
                  </div>
                </div>
              </div>

              <div v-else class="text-center py-16">
                <div
                  class="bg-gray-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4"
                >
                  <svg
                    class="w-10 h-10 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    ></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">No standalone tasks</h3>
                <p class="text-sm text-gray-500 mb-6">
                  All your tasks are already assigned to projects.
                </p>
                <button
                  @click="activeTab = 'create'"
                  class="text-indigo-600 hover:text-indigo-700 font-medium text-sm flex items-center mx-auto"
                >
                  <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 4v16m8-8H4"
                    ></path>
                  </svg>
                  Create a new task instead
                </button>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'remove'" class="max-h-[60vh] overflow-y-auto pr-2">
            <div class="space-y-4">
              <div v-if="loadingProjectTasks" class="text-center py-12">
                <div
                  class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"
                ></div>
                <p class="text-sm text-gray-500 mt-4">Loading project tasks...</p>
              </div>

              <div v-else-if="projectTasks.length > 0" class="space-y-3">
                <template v-for="task in projectTasks" :key="task.id">
                  <div
                    v-if="isTaskOwner(task.id) || isProjectOwner"
                    class="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-xl p-5 hover:border-red-400 hover:shadow-md transition-all"
                  >
                    <div class="flex justify-between items-start">
                      <div class="flex-1">
                        <h4 class="font-semibold text-gray-900 text-lg">{{ task.title }}</h4>
                        <p v-if="task.description" class="text-sm text-gray-600 mt-2 line-clamp-2">
                          {{ task.description }}
                        </p>
                        <div class="flex items-center space-x-4 mt-3">
                          <span
                            :class="[
                              'px-3 py-1 rounded-full text-xs font-semibold',
                              getStatusColor(task.status),
                            ]"
                          >
                            {{ task.status }}
                          </span>
                          <span
                            v-if="task.deadline"
                            class="text-xs text-gray-500 flex items-center"
                          >
                            <svg
                              class="w-4 h-4 mr-1"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                              ></path>
                            </svg>
                            {{ formatDate(task.deadline) }}
                          </span>
                        </div>
                      </div>
                      <button
                        @click="removeTaskFromProject(task.id)"
                        :disabled="removingTask === task.id"
                        class="ml-4 px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white text-sm font-semibold rounded-lg hover:from-red-700 hover:to-red-800 disabled:from-gray-400 disabled:to-gray-400 transition-all shadow-md hover:shadow-lg flex items-center whitespace-nowrap"
                      >
                        <svg
                          v-if="removingTask !== task.id"
                          class="w-4 h-4 mr-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          ></path>
                        </svg>
                        {{ removingTask === task.id ? 'Removing...' : 'Remove' }}
                      </button>
                    </div>
                  </div>
                </template>
              </div>

              <div v-else class="text-center py-16">
                <div
                  class="bg-gray-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4"
                >
                  <svg
                    class="w-10 h-10 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    ></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">No tasks in this project</h3>
                <p class="text-sm text-gray-500">All project tasks have been removed.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue' // <-- Import onMounted
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: Boolean,
  projectId: Number,
  projectDeadline: {
    type: String,
    default: null,
  },
  projectOwnerId: Number,
})

const emit = defineEmits(['close', 'taskAdded'])

const authStore = useAuthStore()
const KONG_API_URL = 'http://localhost:8000'

const activeTab = ref('create')
const creating = ref(false)
const addingTask = ref(null)
const loadingStandaloneTasks = ref(false)
const error = ref(null)
const successMessage = ref(null)

// New task form data
const newTask = ref({
  title: '',
  description: '',
  deadline: '',
  status: 'Unassigned',
  priority: 5,
  is_recurring: false,
  recurrence_interval: 'daily',
  recurrence_days: null,
  recurrence_end_date: null,
})

// --- START: New Collaborator Logic ---
const allUsers = ref([])
const collaboratorIds = ref([]) // Use IDs instead of names
const selectedDepartment = ref('All Departments')
const selectedTeam = ref('All Teams')
const selectedUser = ref('') // This will hold the selected user ID

const standaloneTasks = ref([])

// Fetch all users from the API
const fetchAllUsers = async () => {
  try {
    const response = await fetch(`${KONG_API_URL}/user`)
    if (response.ok) {
      allUsers.value = await response.json()
    } else {
      console.error('Failed to fetch all users.')
      error.value = 'Failed to load user list.'
    }
  } catch (err) {
    console.error('Error fetching all users:', err)
    error.value = 'Error connecting to user service.'
  }
}

// Computed: Get unique departments from all users
const availableDepartments = computed(() => {
  const depts = allUsers.value.map((user) => user.department).filter(Boolean)
  return ['All Departments', ...new Set(depts)]
})

// Computed: Get unique teams, filtered by selected department
const availableTeams = computed(() => {
  let usersInDept = allUsers.value
  if (selectedDepartment.value !== 'All Departments') {
    usersInDept = allUsers.value.filter((user) => user.department === selectedDepartment.value)
  }
  const teams = usersInDept.map((user) => user.team).filter(Boolean)
  return ['All Teams', ...new Set(teams)]
})

// Computed: Filter users for the dropdown
const filteredUsers = computed(() => {
  return allUsers.value.filter((user) => {
    // Filter out the owner (current user, since they are creating the task)
    const isOwner = user.id === authStore.currentUserId
    // Filter out users already added
    const alreadyAdded = collaboratorIds.value.includes(user.id)

    if (isOwner || alreadyAdded) return false

    const matchesDept =
      selectedDepartment.value === 'All Departments' || user.department === selectedDepartment.value
    const matchesTeam = selectedTeam.value === 'All Teams' || user.team === selectedTeam.value

    return matchesDept && matchesTeam
  })
})

// Computed: Get full user objects for the "pills" display
const collaboratorDetails = computed(() => {
  return collaboratorIds.value
    .map((id) => {
      return allUsers.value.find((user) => user.id === id)
    })
    .filter(Boolean) // Filter out undefined users
})
// --- END: New Collaborator Logic ---

// --- START: Date Formatting and Logic ---
const formatDateForInput = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const minDeadline = computed(() => {
  return formatDateForInput(new Date())
})

const minRecurrenceEndDate = computed(() => {
  const baseDate = newTask.value.deadline || minDeadline.value
  const date = new Date(baseDate)
  date.setDate(date.getDate() + 1)
  return formatDateForInput(date)
})

const maxDeadline = computed(() => {
  if (props.projectDeadline) {
    return formatDateForInput(props.projectDeadline)
  }
  if (newTask.value.recurrence_end_date) {
    return formatDateForInput(newTask.value.recurrence_end_date)
  }
  return null
})

watch(
  () => newTask.value.deadline,
  (newDeadline) => {
    if (newTask.value.recurrence_end_date && newDeadline > newTask.value.recurrence_end_date) {
      newTask.value.recurrence_end_date = newDeadline
    }
  },
)
// --- END: Date Formatting and Logic ---

// Watch for modal open
watch(
  () => props.show,
  (isOpen) => {
    if (isOpen) {
      resetForm()
      if (allUsers.value.length === 0) {
        // Only fetch if we don't have users
        fetchAllUsers()
      }
    }
    if (isOpen && activeTab.value === 'add') {
      loadStandaloneTasks()
    }
  },
)

// Watch for tab change
watch(activeTab, (newTab) => {
  if (newTab === 'add' && props.show) {
    loadStandaloneTasks()
  }
  if (newTab === 'remove' && props.show) {
    loadProjectTasks()
  }
})

// --- START: Updated Functions ---
const addCollaborator = () => {
  const userId = parseInt(selectedUser.value) // selectedUser is now an ID
  if (userId && !collaboratorIds.value.includes(userId)) {
    collaboratorIds.value.push(userId)
    selectedUser.value = '' // Reset dropdown
  }
}

const removeCollaborator = (userId) => {
  // Receive ID, not index
  collaboratorIds.value = collaboratorIds.value.filter((id) => id !== userId)
}

const resetForm = () => {
  newTask.value = {
    title: '',
    description: '',
    deadline: '',
    status: 'Unassigned',
    priority: 5,
    is_recurring: false,
    recurrence_interval: 'daily',
    recurrence_days: null,
    recurrence_end_date: null,
  }
  collaboratorIds.value = [] // Reset IDs
  selectedDepartment.value = 'All Departments'
  selectedTeam.value = 'All Teams'
  selectedUser.value = ''
  error.value = null
  successMessage.value = null
}

const createTask = async () => {
  try {
    creating.value = true
    error.value = null
    successMessage.value = null

    if (
      props.projectDeadline &&
      newTask.value.deadline &&
      newTask.value.deadline > formatDateForInput(props.projectDeadline)
    ) {
      throw new Error(
        `Task deadline cannot be later than the project deadline (${formatDate(props.projectDeadline)}).`,
      )
    }

    let payloadData = { ...newTask.value }

    if (payloadData.is_recurring && !payloadData.recurrence_end_date && props.projectDeadline) {
      payloadData.recurrence_end_date = formatDateForInput(props.projectDeadline)
    }

    const response = await fetch(`${KONG_API_URL}/projects/${props.projectId}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...payloadData,
        collaborators_to_add: collaboratorIds.value, // Send IDs
        owner_id: authStore.currentUserId,
        user_id: authStore.currentUserId,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to create task')
    }

    successMessage.value = 'Task created successfully!'
    resetForm()

    setTimeout(() => {
      emit('taskAdded')
      emit('close')
    }, 1000)
  } catch (err) {
    console.error('Error creating task:', err)
    error.value = err.message
  } finally {
    creating.value = false
  }
}
// --- END: Updated Functions ---

const loadStandaloneTasks = async () => {
  try {
    loadingStandaloneTasks.value = true
    error.value = null

    const response = await fetch(
      `${KONG_API_URL}/tasks/standalone?user_id=${authStore.currentUserId}`,
    )

    if (!response.ok) {
      throw new Error('Failed to load tasks')
    }

    standaloneTasks.value = await response.json()
  } catch (err) {
    console.error('Error loading standalone tasks:', err)
    error.value = err.message
  } finally {
    loadingStandaloneTasks.value = false
  }
}

const addTaskToProject = async (taskId) => {
  try {
    addingTask.value = taskId
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/add-to-project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_id: props.projectId,
        user_id: authStore.currentUserId,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to add task to project')
    }

    successMessage.value = 'Task added to project!'
    standaloneTasks.value = standaloneTasks.value.filter((t) => t.id !== taskId)

    setTimeout(() => {
      emit('taskAdded')
      if (standaloneTasks.value.length === 0) {
        emit('close')
      }
    }, 1000)
  } catch (err) {
    console.error('Error adding task to project:', err)
    error.value = err.message
  } finally {
    addingTask.value = null
  }
}

// Remove task from project
const removingTask = ref(null)
const loadingProjectTasks = ref(false)
const projectTasks = ref([])

const isProjectOwner = computed(() => {
  return props.projectOwnerId === authStore.currentUserId
})
const isTaskOwner = (taskId) => {
  const task = projectTasks.value.find((t) => t.id === taskId)
  return task && task.owner_id === authStore.currentUserId
}
// Load project tasks
const loadProjectTasks = async () => {
  try {
    loadingProjectTasks.value = true
    error.value = null

    const response = await fetch(`${KONG_API_URL}/projects/${props.projectId}/tasks`)

    if (!response.ok) {
      throw new Error('Failed to load project tasks')
    }

    projectTasks.value = await response.json()
  } catch (err) {
    console.error('Error loading project tasks:', err)
    error.value = err.message
  } finally {
    loadingProjectTasks.value = false
  }
}
// Remove task from project
const removeTaskFromProject = async (taskId) => {
  if (!confirm('Remove this task from the project?')) {
    return
  }

  try {
    removingTask.value = taskId
    error.value = null
    successMessage.value = null

    const response = await fetch(`${KONG_API_URL}/tasks/${taskId}/remove-from-project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: authStore.currentUserId,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to remove task from project')
    }

    successMessage.value = 'Task removed from project!'
    projectTasks.value = projectTasks.value.filter((t) => t.id !== taskId)

    setTimeout(() => {
      emit('taskAdded')
    }, 1000)
  } catch (err) {
    console.error('Error removing task from project:', err)
    error.value = err.message
  } finally {
    removingTask.value = null
  }
}

const getStatusColor = (status) => {
  const colors = {
    Unassigned: 'bg-gray-100 text-gray-800',
    Ongoing: 'bg-blue-100 text-blue-800',
    'Under Review': 'bg-yellow-100 text-yellow-800',
    Completed: 'bg-green-100 text-green-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Custom scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c7c7c7;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
