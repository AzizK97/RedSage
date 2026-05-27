<template>
  <div class="fixed inset-0 z-50 flex flex-col" style="background: rgba(0,0,0,0.85)">
    <!-- Top bar - never printed -->
    <div class="no-print flex items-center justify-between px-6 py-4 border-b border-white/10 shrink-0"
         style="background: #1a1a1a">
      <div>
        <div class="text-white font-semibold text-base">PDF Preview</div>
        <div class="text-white/50 text-xs mt-0.5">
          This is exactly how your PDF will look when printed
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="handleCancel"
          class="px-4 py-2 text-sm text-white/70 hover:text-white border border-white/20 
                 hover:border-white/40 rounded-lg transition-colors"
        >
          Cancel
        </button>
        <button
          @click="handlePrint"
          class="px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors flex items-center gap-2"
          style="background: #c0392b"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
               fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          Confirm & Download
        </button>
      </div>
    </div>

    <!-- Preview scroll area -->
    <div class="no-print flex-1 overflow-auto flex justify-center py-8 px-4">
      <div class="text-white/40 text-xs mb-4 text-center absolute top-20 left-1/2 -translate-x-1/2">
        Scroll to preview all pages · A4 format
      </div>
      <!-- Scaled preview container -->
      <div
        class="origin-top"
        :style="{
          width: '794px',
          transform: `scale(${previewScale})`,
          transformOrigin: 'top center',
          marginBottom: `${scaledMarginBottom}px`
        }"
      >
        <!-- 
          Live dashboard clone: use a wrapper that shows #dashboard-print-root content.
          We clone the node so the preview reflects actual current state.
        -->
        <div ref="previewCloneRef" class="pdf-preview-clone" style="background:white; min-height: 1123px;" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const emit = defineEmits<{ (e: 'close'): void }>()

const previewCloneRef = ref<HTMLElement | null>(null)
const previewScale = ref(0.7)

// Calculate bottom margin to compensate for CSS scale shrinking the layout height
const scaledMarginBottom = ref(0)

function updateScale() {
  // Scale preview to fit comfortably in the modal width
  // Modal body is viewport width minus padding; preview is 794px wide
  const availableWidth = window.innerWidth - 80
  previewScale.value = Math.min(0.75, availableWidth / 794)
}

function buildPreviewClone() {
  const source = document.getElementById('dashboard-print-root')
  if (!source || !previewCloneRef.value) return

  // Deep clone the dashboard DOM
  const clone = source.cloneNode(true) as HTMLElement

  // Apply print-mode light styles inline on the clone so it looks like the PDF
  clone.style.background = 'white'
  clone.style.color = '#111'
  clone.style.width = '794px'
  clone.style.padding = '24px'
  clone.style.boxSizing = 'border-box'
  clone.style.overflow = 'visible'

  // Add overflow handling styles
  const styleEl = document.createElement('style')
  styleEl.textContent = `
    .pdf-preview-clone * {
      overflow-wrap: break-word;
      word-break: break-word;
    }
    .pdf-preview-clone [class*="truncate"] {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .pdf-preview-clone [class*="flex"] {
      flex-wrap: wrap;
    }
    .pdf-preview-clone [class*="overflow"] {
      overflow: visible !important;
    }
    .pdf-preview-clone table {
      table-layout: fixed;
    }
    .pdf-preview-clone td, .pdf-preview-clone th {
      overflow: hidden;
      text-overflow: ellipsis;
      word-break: break-word;
    }
  `
  clone.appendChild(styleEl)

  // Walk all elements and invert dark backgrounds to white
  clone.querySelectorAll<HTMLElement>('*').forEach(el => {
    const computed = window.getComputedStyle(el)
    const bg = computed.backgroundColor
    // If background is very dark (rgb values all < 60), replace with white
    const match = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
    if (match) {
      const [, r, g, b] = match.map(Number)
      if (r < 60 && g < 60 && b < 60) {
        el.style.backgroundColor = 'white'
        el.style.border = '1px solid #e5e7eb'
      }
    }
    // Fix text colors
    const color = computed.color
    const cm = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
    if (cm) {
      const [, r, g, b] = cm.map(Number)
      // If text is very light (near white), make it dark
      if (r > 200 && g > 200 && b > 200) {
        el.style.color = '#111111'
      } else if (r > 150 && g > 150 && b > 150) {
        el.style.color = '#444444'
      }
    }
    // Remove elements with no-print class
    if (el.classList.contains('no-print')) {
      el.style.display = 'none'
    }
    
    // Fix overflow on scrollable containers
    if (el.classList.contains('custom-scrollbar') || el.classList.contains('overflow-auto') || el.classList.contains('overflow-hidden')) {
      el.style.overflow = 'visible'
      el.style.height = 'auto'
    }
  })

  // Clear the clone container and append
  previewCloneRef.value.innerHTML = ''
  previewCloneRef.value.appendChild(clone)

  // Update margin compensation for scale
  nextTick(() => {
    const cloneHeight = previewCloneRef.value?.scrollHeight ?? 0
    scaledMarginBottom.value = cloneHeight * (previewScale.value - 1)
  })
}

function handlePrint() {
  // Remove clone from DOM temporarily — it must not interfere with print
  if (previewCloneRef.value) previewCloneRef.value.innerHTML = ''

  // Add print-mode to body so @media print stylesheet kicks in
  document.body.classList.add('print-mode')

  window.addEventListener('afterprint', onAfterPrint, { once: true })
  window.print()
}

function onAfterPrint() {
  document.body.classList.remove('print-mode')
  emit('close')
}

function handleCancel() {
  document.body.classList.remove('print-mode')
  emit('close')
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
  // Small delay to ensure dashboard DOM is fully rendered
  setTimeout(buildPreviewClone, 100)
})

onBeforeUnmount(() => {
  document.body.classList.remove('print-mode')
  window.removeEventListener('resize', updateScale)
})
</script>
