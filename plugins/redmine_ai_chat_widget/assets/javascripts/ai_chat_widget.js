(function () {
  const init = function () {
    const root = document.getElementById('ai-chat-widget-root')
    if (!root || document.getElementById('ai-chat-btn')) return

    const backendUrl = (root.dataset.backendUrl || '').replace(/\/$/, '')
    const widgetToken = root.dataset.widgetToken || ''
    const userId = root.dataset.userId || ''
    const userRole = root.dataset.userRole || ''

    if (!userId || !widgetToken || !backendUrl) return

    // Create floating button using vanilla JS (lightweight)
    const btn = document.createElement('button')
    btn.id = 'ai-chat-btn'
    btn.type = 'button'
    btn.className = 'ai-chat-float-btn'
    btn.title = 'AI Chat Assistant'
    btn.setAttribute('aria-label', 'RedSage - Redmine chat assistant')
    btn.innerHTML = [
      '<svg class="ai-chat-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
      '  <path d="M12 8V4H8" />',
      '  <rect width="16" height="12" x="4" y="8" rx="2" />',
      '  <path d="M2 14h2" />',
      '  <path d="M20 14h2" />',
      '  <path d="M15 13v2" />',
      '  <path d="M9 13v2" />',
      '</svg>'
    ].join('');

    // Create container for Vue widget (hidden initially)
    root.innerHTML = `
      <div id="ai-chat-modal" class="ai-chat-modal" style="display: none;">
        <div class="ai-chat-container" id="ai-chat-widget-mount"></div>
      </div>
    `
    const modal = root.querySelector('#ai-chat-modal')
    const container = root.querySelector('#ai-chat-widget-mount')

    document.body.appendChild(btn)

    let vueLoaded = false
    let vueAppMounted = false
    let isOpen = false

    const setOpen = function (nextOpen) {
      isOpen = nextOpen
      modal.style.display = nextOpen ? 'flex' : 'none'
    }

    window.__redmineChatWidgetClose = function () {
      setOpen(false)
    }

    window.__redmineChatWidgetOpen = function () {
      setOpen(true)
    }

    // Load Vue + widget on first button click (lazy loading)
    btn.addEventListener('click', async function () {
      if (!vueLoaded) {
        try {
          setOpen(true)
          btn.disabled = true
          btn.innerHTML = 'Loading...'

          // Try Vite dev server module first (for local development with HMR).
          // Falls back to the production built file under /api/static.
          async function resolveScriptPath() {
            const cleaned = backendUrl.replace(/\/$/, '')
            const productionUrl = `${cleaned}/api/static/chat-widget.js?v=${Date.now()}`

            try {
              const u = new URL(cleaned)
              const hostname = u.hostname || ''
              const port = u.port || ''

              const isContainerHost =
                hostname === 'host.docker.internal' ||
                hostname.endsWith('.docker.internal') ||
                hostname === 'localhost' ||
                (hostname !== 'localhost' && port === '8000')

              console.log('[RedmineChatWidget] Debug:', { hostname, port, isContainerHost, backendUrl })

              if (isContainerHost) {
                const viteUrl = `${u.protocol}//localhost:5173/packages/chat-widget-entry.ts`
                console.log('[RedmineChatWidget] Probing Vite dev server:', viteUrl)
                const res = await fetch(viteUrl, { method: 'HEAD', mode: 'cors' })
                console.log('[RedmineChatWidget] Vite probe result:', res.status, res.ok)
                if (res && res.ok) {
                  console.log('[RedmineChatWidget] Using Vite dev server:', viteUrl)
                  return viteUrl
                }
              }
            } catch (e) {
              console.log('[RedmineChatWidget] URL parsing failed:', e)
            }

            console.log('[RedmineChatWidget] Using production build:', productionUrl)
            return productionUrl
          }

          const script = document.createElement('script')
          script.type = 'module'
          const scriptPath = await resolveScriptPath()
          script.src = scriptPath
          
          script.onload = function () {
            vueLoaded = true
            btn.disabled = false
            btn.innerHTML = [
              '<svg class="ai-chat-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
              '  <path d="M12 8V4H8" />',
              '  <rect width="16" height="12" x="4" y="8" rx="2" />',
              '  <path d="M2 14h2" />',
              '  <path d="M20 14h2" />',
              '  <path d="M15 13v2" />',
              '  <path d="M9 13v2" />',
              '</svg>'
            ].join('');

            // Now that Vue is loaded, initialize the widget
            if (window.initRedmineChatWidget && !vueAppMounted) {
              window.initRedmineChatWidget({
                token: widgetToken,
                userId: userId,
                role: userRole,
                backendUrl: backendUrl,
                containerId: 'ai-chat-widget-mount'
              })
              vueAppMounted = true
            }
          }

          script.onerror = function () {
            btn.disabled = false
            btn.innerHTML = '❌'
            console.error('[RedmineChatWidget] Failed to load chat widget')
          }

          document.head.appendChild(script)
        } catch (error) {
          btn.disabled = false
          console.error('[RedmineChatWidget] Error:', error)
        }
      } else {
        // Toggle modal only after Vue is loaded; do not pre-open first.
        setOpen(!isOpen)
      }
    })
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true })
  } else {
    init()
  }
})()