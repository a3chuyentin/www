import { defineConfig } from 'vite'
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/postcss'
import fs from 'fs'
import path from 'path'

// Custom plugin để copy file CSS vendor
function copyVendorCSS() {
  return {
    name: 'copy-vendor-css',
    closeBundle() {
      const outDir = resolve(__dirname, 'static/dist/vendor')
      
      // Tạo thư mục vendor nếu chưa có
      if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true })
      }
      
      // Copy easymde.min.css
      const easymdeSrc = resolve(__dirname, 'node_modules/easymde/dist/easymde.min.css')
      const easymdeDest = resolve(outDir, 'easymde.min.css')
      if (fs.existsSync(easymdeSrc)) {
        fs.copyFileSync(easymdeSrc, easymdeDest)
        console.log('✓ Copied easymde.min.css')
      }
      
      // Copy github-dark.css
      const highlightSrc = resolve(__dirname, 'node_modules/highlight.js/styles/github-dark.css')
      const highlightDest = resolve(outDir, 'github-dark.css')
      if (fs.existsSync(highlightSrc)) {
        fs.copyFileSync(highlightSrc, highlightDest)
        console.log('✓ Copied github-dark.css')
      }
    }
  }
}

export default defineConfig({
  root: resolve(__dirname),
  plugins: [
    copyVendorCSS()
  ],
  build: {
    outDir: 'static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'static/src/js/main.js'),
        editor: resolve(__dirname, 'static/src/js/editor.js'),
      },
      output: {
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]'
      }
    }
  },
  css: {
    postcss: {
      plugins: [
        tailwindcss(),
      ]
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'static/src'),
    }
  }
})