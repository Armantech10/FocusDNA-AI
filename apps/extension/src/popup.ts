document.addEventListener('DOMContentLoaded', async () => {
  const statusBadge = document.getElementById('statusBadge');
  const activeDomainEl = document.getElementById('activeDomain');
  const togglePauseBtn = document.getElementById('togglePauseBtn') as HTMLButtonElement;

  // 1. Load active tab domain
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0] && tabs[0].url) {
      const url = new URL(tabs[0].url);
      if (activeDomainEl) {
        activeDomainEl.textContent = url.hostname || 'browser.tab';
      }
    }
  } catch (e) {
    if (activeDomainEl) activeDomainEl.textContent = 'browser.tab';
  }

  // 2. Load canonical tracking state from chrome.storage.local (default to true unless explicitly false)
  const storage = await chrome.storage.local.get(['tracking_enabled']);
  let isEnabled = storage.tracking_enabled !== false;

  updateUI(isEnabled);

  // 3. Reactively update popup when chrome.storage changes in background or options
  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName === 'local' && changes.tracking_enabled) {
      isEnabled = changes.tracking_enabled.newValue !== false;
      updateUI(isEnabled);
    }
  });

  // 4. Toggle canonical tracking_enabled on button click
  togglePauseBtn.addEventListener('click', async () => {
    const nextState = !isEnabled;
    isEnabled = nextState;
    await chrome.storage.local.set({ tracking_enabled: nextState });
    updateUI(nextState);
  });

  function updateUI(enabled: boolean) {
    if (enabled) {
      if (statusBadge) {
        statusBadge.textContent = 'Active';
        statusBadge.className = 'status-badge';
      }
      if (togglePauseBtn) {
        togglePauseBtn.textContent = 'Pause Tracking';
        togglePauseBtn.className = 'btn btn-pause';
      }
    } else {
      if (statusBadge) {
        statusBadge.textContent = 'Paused';
        statusBadge.className = 'status-badge paused';
      }
      if (togglePauseBtn) {
        togglePauseBtn.textContent = 'Resume Tracking';
        togglePauseBtn.className = 'btn btn-resume';
      }
    }
  }
});
