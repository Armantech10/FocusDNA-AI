// FocusDNA Web App Bridge Content Script
// Bridges web application session events (FOCUSDNA_SESSION_START, FOCUSDNA_SESSION_END, FOCUSDNA_AUTH_SYNC)
// directly to the extension background service worker.
// Strictly zero keystrokes, no page contents, no form inputs, and no screenshots are captured or read.

window.addEventListener('message', (event) => {
  // Only accept messages from the same window originated by FocusDNA web app
  if (event.source !== window || !event.data || typeof event.data !== 'object') {
    return;
  }

  if (event.data.source === 'FOCUSDNA_WEB_APP') {
    try {
      chrome.runtime.sendMessage(event.data, () => {
        if (chrome.runtime.lastError) {
          // Extension background service worker may be initializing
        }
      });
    } catch (e) {
      // Extension context invalidated/reloaded
    }
  }
});
