/**
 * Standalone chat widget for Redmine plugin
 * Exports a single global function to initialize the chat
 * Creates a clean entry point that Vue can build seperatly.
 * When loaded, it exposes ONE function to window.
 */
import { createApp } from 'vue';
import PluginChatWrapper from './components/pluginUI/PluginChatWrapper.vue';
import widgetStylesHref from './components/pluginUI/plugin-widget.css?url';

function ensureWidgetStyles(backendUrl?: string) {
  if (document.getElementById('redmine-chat-widget-styles')) {
    return;
  }

  // If a backendUrl is provided, prefer serving the emitted CSS from the
  // backend static mount. This keeps the widget robust when built without
  // the `widget` build mode or when filenames/hashes change.
  let href = widgetStylesHref;
  try {
    const parts = String(widgetStylesHref).split('/');
    const fileName = parts.pop() || parts[parts.length - 1] || widgetStylesHref;
    if (backendUrl) {
      const cleaned = backendUrl.replace(/\/$/, '');
      href = `${cleaned}/api/static/${fileName}`;
    }
  } catch (err) {
    // fallback to compiled url
    href = widgetStylesHref;
  }

  const link = document.createElement('link');
  link.id = 'redmine-chat-widget-styles';
  link.rel = 'stylesheet';
  link.href = href;
  document.head.appendChild(link);
}

declare global {
  interface Window {
    initRedmineChatWidget: (options: {
      token: string;
      userId: string;
      role: 'admin' | 'project_manager';
      backendUrl?: string;
      containerId?: string;
    }) => void;
    __updateModalClass?: (className: string) => void;
  }
}

function mountWidget(options: {
  token: string;
  userId: string;
  role: 'admin' | 'project_manager';
  backendUrl?: string;
  containerId?: string;
}) {
  const containerId = options.containerId || 'ai-chat-widget-mount';
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`[RedmineChatWidget] Container #${containerId} not found.`);
    return;
  }

  ensureWidgetStyles(options.backendUrl);

  container.innerHTML = '';
  container.style.width = '100%';
  container.style.height = '100%';

  const appRoot = document.createElement('div');
  appRoot.id = 'app';
  appRoot.style.width = '100%';
  appRoot.style.height = '100%';
  container.appendChild(appRoot);

  const app = createApp(PluginChatWrapper, {
    token: options.token,
    userId: options.userId,
    role: options.role,
  });

  app.mount(appRoot);
}

window.initRedmineChatWidget = function (options) {
  try {
    mountWidget(options);
  } catch (error) {
    console.error('[RedmineChatWidget] Failed to mount widget:', error);
  }
};