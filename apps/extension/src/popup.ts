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

  // 2. Load storage state
  const storage = await chrome.storage.local.get(['is_tracking_paused']);
  let isPaused = storage.is_tracking_paused || false;

  updateUI(isPaused);

  togglePauseBtn.addEventListener('click', async () => {
    isPaused = !isPaused;
    await chrome.storage.local.set({ is_tracking_paused: isPaused });
    updateUI(isPaused);
  });

  function updateUI(paused: boolean) {
    if (paused) {
      if (statusBadge) {
        statusBadge.textContent = 'Paused';
        statusBadge.className = 'status-badge paused';
      }
      togglePauseBtn.textContent = 'Resume Tracking';
      togglePauseBtn.className = 'btn btn-resume';
    } else {
      if (statusBadge) {
        statusBadge.textContent = 'Active';
        statusBadge.className = 'status-badge';
      }
      togglePauseBtn.textContent = 'Pause Tracking';
      togglePauseBtn.className = 'btn btn-pause';
    }
  }
});
