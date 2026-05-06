<script setup lang="ts">
import { ref } from "vue";
import type { ConversationSummary } from "../composables/useThreads";
import { 
  MoreVertical, 
  Trash2, 
  Plus,
  MessageSquare,
  Clock,
  Edit2
} from 'lucide-vue-next';

const props = defineProps<{
  conversations: ConversationSummary[];
  activeThreadId: string;
}>();

const emit = defineEmits<{
  (e: "select", threadId: string): void;
  (e: "new"): void;
  (e: "delete", threadId: string): void;
}>();

const openMenu = ref<string | null>(null);

function groupConversationsByTime(conversations: ConversationSummary[]) {
  const now = Date.now();
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);
  const sevenDaysAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
  const thirtyDaysAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);

  const groups: Record<string, ConversationSummary[]> = {
    today: [],
    sevenDays: [],
    thirtyDays: [],
    older: [],
  };

  conversations.forEach((conv) => {
    const convDate = new Date(conv.updatedAt);
    convDate.setHours(0, 0, 0, 0);

    if (convDate.getTime() === today.getTime()) {
      groups.today.push(conv);
    } else if (conv.updatedAt > sevenDaysAgo.getTime()) {
      groups.sevenDays.push(conv);
    } else if (conv.updatedAt > thirtyDaysAgo.getTime()) {
      groups.thirtyDays.push(conv);
    } else {
      groups.older.push(conv);
    }
  });

  return groups;
}

function toggleMenu(threadId: string) {
  openMenu.value = openMenu.value === threadId ? null : threadId;
}

function handleDelete(threadId: string) {
  emit("delete", threadId);
  openMenu.value = null;
}

function handleRename(threadId: string) {
  console.log("Rename conversation:", threadId);
  openMenu.value = null;
}
</script>

<template>
  <aside class="w-72 min-w-[288px] h-full bg-surface-950 border-r border-surface-800 flex flex-col z-30">
    <div class="p-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-2 text-surface-200">
        <MessageSquare :size="18" class="text-sage-400" />
        <h2 class="text-sm font-bold tracking-tight">Conversations</h2>
      </div>
      <button 
        @click="emit('new')" 
        class="w-9 h-9 rounded-xl bg-sage-500 hover:bg-sage-400 text-surface-950 flex items-center justify-center transition-all shadow-lg shadow-sage-900/20 active:scale-95"
        aria-label="New conversation"
      >
        <Plus :size="20" stroke-width="2.5" />
      </button>
    </div>

    <div class="flex-1 overflow-auto px-4 pb-6 space-y-8 custom-scrollbar">
      <template v-for="(group, key) in groupConversationsByTime(props.conversations)" :key="key">
        <div v-if="group.length > 0" class="flex flex-col gap-1.5">
          <div class="flex items-center gap-2 px-3 mb-2">
            <Clock :size="10" class="text-surface-600" />
            <span class="text-[10px] font-bold text-surface-500 uppercase tracking-widest">
              {{ key === 'today' ? 'Today' : key === 'sevenDays' ? 'Previous 7 days' : key === 'thirtyDays' ? 'Previous 30 days' : 'Older' }}
            </span>
          </div>

          <div
            v-for="conversation in group"
            :key="conversation.id"
            :class="[
              'group relative flex items-center gap-2 rounded-xl transition-all duration-200 border cursor-pointer h-12',
              conversation.id === props.activeThreadId 
                ? 'bg-surface-800/60 border-surface-700 text-white' 
                : 'border-transparent text-surface-400 hover:bg-surface-900 hover:text-surface-200'
            ]"
          >
            <button
              class="flex-1 px-4 py-3 h-full text-left min-w-0"
              type="button"
              @click="emit('select', conversation.id)"
            >
              <p class="text-xs font-semibold truncate">{{ conversation.title || 'Untitled Chat' }}</p>
            </button>

            <div class="px-2">
              <button
                class="w-8 h-8 rounded-lg flex items-center justify-center text-surface-600 hover:text-white hover:bg-surface-800 transition-all opacity-0 group-hover:opacity-100"
                type="button"
                @click.stop="toggleMenu(conversation.id)"
              >
                <MoreVertical :size="14" />
              </button>

              <div v-if="openMenu === conversation.id" class="absolute right-2 top-10 w-48 bg-surface-900 border border-surface-800 rounded-xl shadow-2xl z-50 overflow-hidden py-1 backdrop-blur-xl animate-scale-in origin-top-right">
                <button
                  type="button"
                  class="w-full text-left px-4 py-2.5 text-xs font-bold text-surface-300 hover:bg-surface-800 hover:text-white transition-all flex items-center gap-3"
                  @click.stop="handleRename(conversation.id)"
                >
                  <Edit2 :size="14" /> Rename
                </button>
                <button
                  type="button"
                  class="w-full text-left px-4 py-2.5 text-xs font-bold text-red-400 hover:bg-red-500/10 transition-all flex items-center gap-3"
                  @click.stop="handleDelete(conversation.id)"
                >
                  <Trash2 :size="14" /> Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
      
      <div v-if="props.conversations.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
        <div class="w-12 h-12 rounded-2xl bg-surface-900 flex items-center justify-center mb-4 border border-surface-800">
          <MessageSquare :size="20" class="text-surface-600 opacity-30" />
        </div>
        <p class="text-xs font-bold text-surface-600 uppercase tracking-widest">No conversations</p>
      </div>
    </div>
  </aside>
</template>

<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2a2d29;
  border-radius: 99px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #3c5439;
}
@keyframes scale-in {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
.animate-scale-in {
  animation: scale-in 0.15s ease-out;
}
</style>

