<script setup lang="ts">
import { ref } from "vue";
import type { ConversationSummary } from "../composables/useThreads";
import { 
  MoreVertical, 
  Trash, 
  ChevronsLeft, 
  Plus
} from '@lucide/vue';

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

const isCollapsed = ref(false)

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
  // Placeholder for rename functionality
  console.log("Rename conversation:", threadId);
  openMenu.value = null;
}
</script>

<template>
  <aside :class="{ sidebar: true, collapsed: isCollapsed }">
    <div class="sidebar-header">
      <div v-show="!isCollapsed" class="header-content">
        <h2>All chats</h2>
      </div>
      <div class="header-actions">
        <button class="new-btn" @click="emit('new')" aria-label="Create new conversation">
          <Plus/>
        </button>
      </div>
    </div>

    <div v-show="!isCollapsed" class="conversation-list">
      <template v-for="(group, key) in groupConversationsByTime(props.conversations)" :key="key">
        <div v-if="group.length > 0" class="conversation-group">
          <div class="group-label">
            <span v-if="key === 'today'">Today</span>
            <span v-else-if="key === 'sevenDays'">Previous 7 days</span>
            <span v-else-if="key === 'thirtyDays'">Previous 30 days</span>
            <span v-else>Older</span>
          </div>

          <div
            v-for="conversation in group"
            :key="conversation.id"
            class="conversation-item"
            :class="{ active: conversation.id === props.activeThreadId }"
          >
            <button
              class="conversation-select"
              type="button"
              @click="emit('select', conversation.id)"
            >
              <div class="conversation-title">{{ conversation.title }}</div>
            </button>

            <div class="menu-container">
              <button
                class="menu-btn"
                type="button"
                @click="toggleMenu(conversation.id)"
                aria-label="Options"
              >
                <MoreVertical :size="16" />
              </button>

              <div v-if="openMenu === conversation.id" class="menu-dropdown">
                <button
                  type="button"
                  class="menu-item"
                  @click="handleRename(conversation.id)"
                >
                  Rename
                </button>
                <button
                  type="button"
                  class="menu-item delete-item"
                  @click="handleDelete(conversation.id)"
                >
                    <Trash :size="15"/>
                    Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div class="sidebar-footer">
      <button @click="isCollapsed = !isCollapsed" class="collapse-btn">
        <ChevronsLeft :class="{ rotated: isCollapsed }" />
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: relative;
  width: 280px;
  min-width: 280px;
  height: 100%;
  background: var(--bg-secondary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid var(--border-subtle);
  transition: width 280ms ease, min-width 280ms ease;
}

.sidebar.collapsed {
  width: 70px;
  min-width: 70px;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
}

.sidebar.collapsed .header-actions {
  flex: 1;
  justify-content: center;
  margin-left: 0;
}

.sidebar.collapsed .sidebar-footer {
  padding: var(--space-sm);
}

.sidebar-header {
  padding: var(--space-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-md);
}

.header-content {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  transition: max-width 240ms ease, opacity 180ms ease, transform 240ms ease;
}

h2 {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-toggle {
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition-fast);
}

.dropdown-toggle:hover {
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.new-btn {
  border: none;
  background: #d94a3a;
  width: 36px;
  height: 36px;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 180ms ease, background-color 180ms ease, opacity 180ms ease;
}

.new-btn:hover {
  background: #e85844;
}

.conversation-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 0 var(--space-md);
}

.conversation-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  margin-top: var(--space-lg);
}

.conversation-group:first-child {
  margin-top: 0;
}

.group-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  padding: var(--space-sm) var(--space-md);
  text-transform: capitalize;
  font-weight: 500;
}

.conversation-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: var(--radius-md);
  transition: background-color 180ms ease, transform 180ms ease, padding 180ms ease;
  padding: var(--space-sm);
}

.conversation-item:hover {
  background: var(--bg-tertiary);
}

.conversation-item.active {
  background: var(--bg-tertiary);
}

.conversation-select {
  flex: 1;
  text-align: left;
  border: none;
  background: transparent;
  color: inherit;
  padding: var(--space-xs) var(--space-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--text-sm);
  transition: gap 240ms ease, padding 240ms ease, opacity 180ms ease, transform 240ms ease;
  min-width: 0;
}

.conversation-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 400;
  transition: opacity 180ms ease, transform 240ms ease, max-width 240ms ease;
}

.menu-container {
  position: relative;
}

.menu-btn {
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  padding: var(--space-xs);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: opacity 180ms ease, transform 180ms ease, background-color 180ms ease, color 180ms ease;
}

.menu-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.menu-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  min-width: 120px;
  margin-top: var(--space-xs);
  overflow: hidden;
}

.menu-item {
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-md);
  cursor: pointer;
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
}

.menu-item:hover {
  background: var(--bg-tertiary);
}

.menu-item.delete-item {
  color: var(--accent-red);
}

.menu-item.delete-item:hover {
  background: rgba(239, 68, 68, 0.1);
}

.collapse-btn {
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: var(--space-md);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: background-color 180ms ease, color 180ms ease, transform 180ms ease;
}

.collapse-btn:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-subtle);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

.sidebar-footer {
  padding: var(--space-md);
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
  width: 100%;
}

/* .sidebar.collapsed .header-content,
.sidebar.collapsed .conversation-title,
.sidebar.collapsed .group-label,
.sidebar.collapsed .menu-btn {
  opacity: 0;
  transform: translateX(-8px);
  pointer-events: none;
} */

/* .sidebar.collapsed .header-content,
.sidebar.collapsed .group-label {
  max-width: 0;
} */

/* .sidebar.collapsed .conversation-item {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
} */

/* .sidebar.collapsed .conversation-select {
  padding-left: 0;
  padding-right: 0;
} */

/* .sidebar.collapsed .menu-container {
  width: 0;
  overflow: hidden;
} */

.collapse-btn svg {
  transition: transform 240ms ease-out;
}

.collapse-btn .rotated {
  transform: rotate(180deg);
}

.sidebar.collapsed .new-btn {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
}

</style>
