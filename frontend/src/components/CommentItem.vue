<template>
  <div class="comment-item">
    <div class="flex space-x-3">
      <!-- Avatar -->
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
          <span class="text-indigo-600 font-medium text-sm">
            {{ getAuthorInitials(authorName) }}
          </span>
        </div>
      </div>

      <!-- Comment Content -->
      <div class="flex-1 min-w-0">
        <div class="bg-gray-50 rounded-lg p-4">
          <!-- Comment Header -->
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2">
              <span class="text-sm font-medium text-gray-900">
                {{ authorName }}
              </span>
              <span class="text-xs text-gray-500">
                {{ formatTime(comment.created_at) }}
              </span>
            </div>
            <button
              v-if="canDelete"
              @click="$emit('delete', comment.id)"
              class="text-red-600 hover:text-red-800 text-xs"
              title="Delete comment"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>

          <!-- Comment Body -->
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ comment.body }}</p>
        </div>

        <!-- Reply Button -->
        <div class="mt-2 flex items-center space-x-4">
          <button
            @click="showReplyForm = !showReplyForm"
            class="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
              />
            </svg>
            {{ showReplyForm ? 'Cancel' : 'Reply' }}
          </button>
          <span v-if="comment.reply_count > 0" class="text-xs text-gray-500">
            {{ comment.reply_count }} {{ comment.reply_count === 1 ? 'reply' : 'replies' }}
          </span>
        </div>

        <!-- Reply Form -->
        <div v-if="showReplyForm" class="mt-3 ml-4">
          <div class="bg-white border border-gray-200 rounded-lg p-3">
            <Mentionable
              :keys="['@']"
              :items="
                collaboratorDetails.map((c) => ({
                  value: c.username,
                  label: c.name,
                  user_id: c.user_id,
                  role: c.role,
                }))
              "
              offset="6"
              insert-space
            >
              <textarea
                v-model="replyText"
                placeholder="Write a reply..."
                rows="3"
                class="w-full text-sm border-0 focus:ring-0 resize-none"
                @keydown.meta.enter="submitReply"
                @keydown.ctrl.enter="submitReply"
              >
              </textarea>
              <template #item-@="{ item, isSelected }">
                <div
                  :class="[
                    'flex items-center p-2 space-x-3 cursor-pointer rounded-md transition-colors duration-150 ease-in-out',
                    isSelected ? 'bg-indigo-100' : 'hover:bg-gray-50',
                  ]"
                >
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
            <div class="flex justify-end space-x-2 mt-2">
              <button
                @click="showReplyForm = false"
                class="px-3 py-1 text-xs text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                @click="submitReply"
                :disabled="!replyText.trim() || submittingReply"
                class="px-3 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ submittingReply ? 'Posting...' : 'Reply' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Nested Replies -->
        <div
          v-if="comment.replies && comment.replies.length > 0"
          class="mt-4 ml-4 space-y-4 border-l-2 border-gray-200 pl-4"
        >
          <CommentItem
            v-for="reply in comment.replies"
            :key="reply.id"
            :comment="reply"
            :current-user-id="currentUserId"
            :collaborator-details="collaboratorDetails"
            @reply="$emit('reply', $event)"
            @delete="$emit('delete', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Mentionable } from 'vue-mention'
import 'floating-vue/dist/style.css'

const props = defineProps({
  comment: {
    type: Object,
    required: true,
  },
  currentUserId: {
    type: Number,
    default: null,
  },
  collaboratorDetails: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['reply', 'delete'])

const showReplyForm = ref(false)
const replyText = ref('')
const submittingReply = ref(false)

const author = computed(() => {
  return props.collaboratorDetails.find((c) => c.user_id === props.comment.author_id)
})
const authorName = computed(() => {
  return author.value ? author.value.name : `${props.comment.author_id}`
})

const canDelete = computed(() => {
  return props.currentUserId === props.comment.author_id
})

const getAuthorInitials = (authorId) => {
  return `${authorId.charAt(0).toUpperCase()}${authorId.charAt(1) ? authorId.charAt(1).toUpperCase() : ''}`
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''

  // Ensure timestamp is treated as UTC and convert to user's local timezone
  let date
  if (timestamp.includes('Z') || timestamp.includes('+')) {
    // Already has timezone info
    date = new Date(timestamp)
  } else {
    // Assume UTC and append 'Z'
    date = new Date(timestamp + 'Z')
  }

  // Format: "Oct 6, 2025, 9:21 PM" (in user's timezone)
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

const submitReply = async () => {
  if (!replyText.value.trim() || submittingReply.value) return

  submittingReply.value = true
  try {
    await emit('reply', {
      parentCommentId: props.comment.id,
      body: replyText.value.trim(),
    })
    replyText.value = ''
    showReplyForm.value = false
  } finally {
    submittingReply.value = false
  }
}
</script>

<style scoped>
.comment-item {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
