<script setup lang="ts">
import { ref } from "vue";
import { ChevronsLeft, LayoutDashboard, Bot, User, LogOut, Leaf } from "lucide-vue-next";

const props = defineProps<{
  role: "admin" | "project_manager";
  currentView: "dashboard" | "chat" | "profile";
}>();

const emit = defineEmits<{
  (event: "navigate", view: "dashboard" | "chat" | "profile"): void;
  (event: "logout"): void;
}>();

const isCollapsed = ref(false);

function roleLabel() {
  return props.role === "admin" ? "Admin" : "Project Manager";
}
</script>

<template>
  <aside 
    :class="[
      'h-full bg-surface-950 border-r border-surface-800 px-4 py-6 flex flex-col gap-8 transition-all duration-300 ease-in-out z-40',
      isCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <div class="flex items-center justify-between gap-3">
      <div v-show="!isCollapsed" class="flex items-center gap-2.5 overflow-hidden">
        <div class="w-8 h-8 shrink-0 rounded-lg bg-gradient-to-br from-sage-400 to-copper-500 flex items-center justify-center shadow-lg shadow-sage-900/40">
          <Leaf :size="18" class="text-white" />
        </div>
        <div class="flex flex-col leading-tight">
          <span class="font-bold text-white tracking-tight">RedSage</span>
          <span class="text-[10px] text-surface-500 uppercase tracking-widest font-semibold">{{ roleLabel() }}</span>
        </div>
      </div>
      <button 
        class="w-8 h-8 rounded-lg flex items-center justify-center text-surface-400 hover:text-white hover:bg-surface-800 transition-colors"
        type="button" 
        @click="isCollapsed = !isCollapsed" 
        aria-label="Toggle sidebar"
      >
        <ChevronsLeft :class="['transition-transform duration-300', isCollapsed ? 'rotate-180' : '']" :size="18" />
      </button>
    </div>

    <nav class="flex flex-col gap-1.5 flex-1">
      <button
        v-for="item in [
          { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
          { id: 'chat', label: 'Chatbot', icon: Bot },
          { id: 'profile', label: 'Profile', icon: User },
        ]"
        :key="item.id"
        :class="[
          'group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-sm font-medium h-11 overflow-hidden',
          currentView === item.id 
            ? 'bg-sage-500/10 text-sage-300 border border-sage-500/20' 
            : 'text-surface-400 hover:text-surface-200 hover:bg-surface-900 border border-transparent'
        ]"
        type="button"
        @click="emit('navigate', item.id as any)"
        :title="isCollapsed ? item.label : ''"
      >
        <component :is="item.icon" :size="18" :class="['shrink-0', currentView === item.id ? 'text-sage-400' : 'group-hover:text-sage-400']" />
        <span v-show="!isCollapsed" class="whitespace-nowrap">{{ item.label }}</span>
      </button>
    </nav>

    <div class="mt-auto pt-4 border-t border-surface-800">
      <button 
        class="group flex items-center gap-3 px-3 py-2.5 rounded-xl text-surface-400 hover:text-red-400 hover:bg-red-500/5 transition-all text-sm font-medium w-full h-11 overflow-hidden" 
        type="button" 
        @click="emit('logout')"
        :title="isCollapsed ? 'Log out' : ''"
      >
        <LogOut :size="18" class="shrink-0 group-hover:text-red-400" />
        <span v-show="!isCollapsed">Log out</span>
      </button>
    </div>
  </aside>
</template>

