import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'
import path from 'path'

export default defineConfig(({ mode }) => ({
  base: mode === 'widget' ? '/api/static/' : '/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@redsage/ui-core': path.resolve(__dirname, './packages/ui-core/src'),
      '@redsage/api-client': path.resolve(__dirname, './packages/api-client/src'),
      '@redsage/platform': path.resolve(__dirname, './packages/platform/src'),
      '@redsage/plugin-widget': path.resolve(__dirname, './packages/plugin-widget/src'),
    },
  },
  css: {
    postcss: {
      plugins: [
        tailwindcss(),
        autoprefixer(),
      ],
    },
  },
  build: {
    emptyOutDir: true,
    cssCodeSplit: true,
    outDir: mode === 'widget' ? 'dist-widget' : 'dist',
    rollupOptions: mode === 'widget'
      ? {
        input: path.resolve(__dirname, 'packages/chat-widget-entry.ts'),
        output: {
          entryFileNames: 'chat-widget.js',
          chunkFileNames: 'chat-widget-[name].js',
          assetFileNames: (assetInfo) => {
            if (assetInfo.name?.endsWith('.css')) {
              return 'chat-widget.css'
            }

            return 'assets/[name][extname]'
          },
        },
      }
      : {
        input: {
          main: path.resolve(__dirname, 'index.html'),
        },
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash][extname]',
        },
      },
  },
}))