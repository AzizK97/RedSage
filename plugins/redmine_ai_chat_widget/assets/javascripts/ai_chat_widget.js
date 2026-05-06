(function () {
  const init = function () {
    const root = document.getElementById("ai-chat-widget-root");
    if (!root || document.getElementById("ai-chat-btn")) return;

    const backendUrl = (root.dataset.backendUrl || "").replace(/\/$/, "");
    const widgetToken = root.dataset.widgetToken || "";
    const userId = root.dataset.userId || "";
    const userLogin = root.dataset.userLogin || "";

    if (!userId || !userLogin) {
      return; 
    }

    if (!backendUrl || !widgetToken) {
      return;
    }

    const btn = document.createElement("button");
    btn.id = "ai-chat-btn";
    btn.type = "button";
    btn.title = "AI Chat Assistant";
    btn.setAttribute("aria-label", "Open AI chat assistant");
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

    const panel = document.createElement("div");
    panel.id = "ai-chat-panel";
    panel.setAttribute("aria-hidden", "true");
    panel.innerHTML = [
      '<div class="ai-chat-header">',
      '  <h3>RedSage AI Assistant</h3>',
      '  <button type="button" class="ai-chat-close" aria-label="Close chat">&times;</button>',
      '</div>',
      '<div class="ai-chat-messages" id="ai-chat-messages" aria-live="polite"></div>',
      '<div class="ai-chat-input-area">',
      '  <input type="text" class="ai-chat-input" id="ai-chat-input" placeholder="Type your question..." autocomplete="off" />',
      '  <button type="button" class="ai-chat-send" id="ai-chat-send">Send</button>',
      '</div>'
    ].join('');

    document.body.appendChild(btn);
    document.body.appendChild(panel);

    const messagesDiv = panel.querySelector('#ai-chat-messages');
    const input = panel.querySelector('#ai-chat-input');
    const sendBtn = panel.querySelector('#ai-chat-send');
    const closeBtn = panel.querySelector('.ai-chat-close');

    function escapeHtml(text) {
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function addMessage(content, kind) {
      const msgEl = document.createElement('div');
      msgEl.className = `ai-chat-message ${kind}`;

      const contentEl = document.createElement('div');
      contentEl.className = 'ai-chat-message-content';
      contentEl.innerHTML = escapeHtml(content);

      msgEl.appendChild(contentEl);
      messagesDiv.appendChild(msgEl);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function setPanelOpen(isOpen) {
      panel.classList.toggle('active', isOpen);
      panel.setAttribute('aria-hidden', String(!isOpen));
      if (isOpen) input.focus();
    }

    function togglePanel() {
      setPanelOpen(!panel.classList.contains('active'));
    }

    function setBusy(isBusy) {
      sendBtn.disabled = isBusy;
      input.disabled = isBusy;
      btn.disabled = isBusy;
    }

    async function sendMessage() {
      const message = input.value.trim();
      if (!message) return;

      addMessage(message, 'user');
      input.value = '';
      setBusy(true);

      try {
        const response = await fetch(`${backendUrl}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${widgetToken}`
          },
          body: JSON.stringify({
            message: message,
            thread_id: "default"
          })
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        addMessage(data.response || 'No response from server.', 'bot');
      } catch (error) {
        addMessage(`Error: ${error.message}. Check the backend at ${backendUrl}.`, 'bot');
      } finally {
        setBusy(false);
        input.focus();
      }
    }

    btn.addEventListener('click', togglePanel);
    closeBtn.addEventListener('click', function () {
      setPanelOpen(false);
    });
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
      }
    });

    addMessage('Hello! How can I help you with your Redmine projects today?', 'bot');
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
