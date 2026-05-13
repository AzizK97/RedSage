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
        input: path.resolve(__dirname, 'src/chat-widget-entry.ts'),
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