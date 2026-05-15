<script setup lang="ts">
import { ref } from 'vue'
import { MessageSquare, Trash2, Clock, Pin } from 'lucide-vue-next'

interface Thread {
  id: string
  title: string
  timestamp: string
  preview: string
  messageCount: number
  isPinned: boolean
}

defineEmits<{
  (e: 'select', threadId: string): void
  (e: 'delete', threadId: string): void
}>()

const activeThreadId = ref<string | null>(null)

// Placeholder threads
const threads = ref<Thread[]>([
  {
    id: 'thread-1',
    title: 'Project Kickoff Discussion',
    timestamp: '2 hours ago',
    preview: 'Reviewed Q2 roadmap and resource allocation...',
    messageCount: 12,
    isPinned: true,
  },
  {
    id: 'thread-2',
    title: 'Bug Triage - Critical Issues',
    timestamp: '4 hours ago',
    preview: 'Prioritized and assigned 5 critical production bugs...',
    messageCount: 8,
    isPinned: false,
  },
  {
    id: 'thread-3',
    title: 'API Performance Analysis',
    timestamp: 'Yesterday',
    preview: 'Analyzed slow endpoint, identified caching opportunity...',
    messageCount: 15,
    isPinned: false,
  },
  {
    id: 'thread-4',
    title: 'Team Onboarding Questions',
    timestamp: '2 days ago',
    preview: 'Answered setup questions for new developer...',
    messageCount: 5,
    isPinned: false,
  },
])

const handleSelect = (threadId: string) => {
  activeThreadId.value = threadId
}

const handleDelete = (threadId: string) => {
  if (confirm('Delete this conversation?')) {
    threads.value = threads.value.filter(t => t.id !== threadId)
    activeThreadId.value = null
  }
}
</script>

<template>
  <div class="h-full flex flex-col bg-surface-950">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-surface-800 bg-surface-950/50 shrink-0">
      <h2 class="text-sm font-bold text-surface-200 flex items-center gap-2">
        <MessageSquare :size="16" class="text-sage-500" />
        Conversations
      </h2>
      <p class="text-xs text-surface-600 mt-1">{{ threads.length }} threads</p>
    </div>

    <!-- Threads List -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="divide-y divide-surface-800">
        <button
          v-for="thread in threads"
          :key="thread.id"
          type="button"
          class="w-full text-left px-4 py-3 hover:bg-surface-900/50 transition-colors group border-l-2 border-transparent hover:border-l-sage-500"
          :class="{ 'bg-surface-900 border-l-sage-500': activeThreadId === thread.id }"
          @click="handleSelect(thread.id)"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              <h3 class="text-sm font-semibold text-surface-100 truncate">
                {{ thread.title }}
              </h3>
              <Pin
                v-if="thread.isPinned"
                :size="12"
                class="shrink-0 text-sage-500 fill-sage-500"
              />
            </div>
            <button
              v-if="activeThreadId === thread.id"
              type="button"
              class="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-surface-800 rounded"
              @click.stop="handleDelete(thread.id)"
              title="Delete thread"
            >
              <Trash2 :size="14" class="text-red-500" />
            </button>
          </div>

          <p class="text-xs text-surface-400 truncate mb-2">{{ thread.preview }}</p>

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3 text-xs text-surface-600">
              <span class="flex items-center gap-1">
                <MessageSquare :size="12" />
                {{ thread.messageCount }}
              </span>
              <span class="flex items-center gap-1">
                <Clock :size="12" />
                {{ thread.timestamp }}
              </span>
            </div>
          </div>
        </button>
      </div>

      <!-- Empty state -->
      <div v-if="threads.length === 0" class="flex-1 flex items-center justify-center p-8">
        <div class="text-center">
          <MessageSquare :size="32" class="mx-auto mb-3 text-surface-700" />
          <p class="text-sm text-surface-600 font-medium">No conversations yet</p>
          <p class="text-xs text-surface-700 mt-1">Start a new chat to begin</p>
        </div>
      </div>
    </div>
  </div>
</template>