/**
 * Standalone chat widget for Redmine plugin
 * Exports a single global function to initialize the chat
 * Creates a clean entry point that Vue can build separately.
 * When loaded, it exposes ONE function to window.
 */
import { createApp } from 'vue';
import PluginChatWrapper from './components/pluginUI/PluginChatWrapper.vue';
import widgetStylesHref from './widget/chat-widget.css?url';

function ensureWidgetStyles(backendUrl?: string) {
  if (document.getElementById('redmine-chat-widget-styles')) {
    return;
  }

  let href = widgetStylesHref;
  try {
    href = backendUrl ? new URL(widgetStylesHref, backendUrl).toString() : widgetStylesHref;
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