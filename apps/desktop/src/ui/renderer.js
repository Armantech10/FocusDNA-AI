document.addEventListener('DOMContentLoaded', async () => {
  const trackingToggle = document.getElementById('tracking-toggle');
  const trackingStatusText = document.getElementById('tracking-status-text');
  const currentFocusState = document.getElementById('current-focus-state');
  const currentScore = document.getElementById('current-score');
  const activeAppName = document.getElementById('active-app-name');
  const queuedCount = document.getElementById('queued-count');
  const syncStatus = document.getElementById('sync-status');
  const syncText = document.getElementById('sync-text');
  const btnPurge = document.getElementById('btn-purge');

  // Load initial desktop state
  if (window.electronAPI) {
    const initialState = await window.electronAPI.getDesktopState();
    updateUI(initialState);

    // Listen for real-time state updates
    window.electronAPI.onStateUpdate((state) => {
      updateUI(state);
    });
  }

  function updateUI(state) {
    if (!state) return;

    // Tracking toggle state
    trackingToggle.checked = state.isTracking;
    if (state.isPaused) {
      trackingStatusText.textContent = `Paused (${state.pauseRemainingMins}m remaining)`;
      trackingStatusText.style.color = '#f59e0b';
    } else if (state.isTracking) {
      trackingStatusText.textContent = 'Active (Monitoring)';
      trackingStatusText.style.color = '#10b981';
    } else {
      trackingStatusText.textContent = 'Disabled (Off)';
      trackingStatusText.style.color = '#ef4444';
    }

    // Active App & Score
    activeAppName.textContent = state.activeApp || 'Finder';
    currentScore.textContent = state.focusScore || 85;
    currentFocusState.textContent = (state.focusScore || 85) >= 65 ? 'FOCUSED' : 'DISTRACTED';
    currentFocusState.style.color = (state.focusScore || 85) >= 65 ? '#10b981' : '#ef4444';

    // Sync & Offline Queue
    queuedCount.textContent = state.queuedEventsCount || 0;
    if (state.isOnline) {
      syncStatus.className = 'status-badge online';
      syncText.textContent = 'Online';
    } else {
      syncStatus.className = 'status-badge offline';
      syncText.textContent = `Offline (${state.queuedEventsCount} queued)`;
    }
  }

  // Event Listeners
  trackingToggle.addEventListener('change', async (e) => {
    if (window.electronAPI) {
      await window.electronAPI.toggleTracking(e.target.checked);
    }
  });

  document.querySelectorAll('.pause-btn').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const mins = parseInt(e.target.getAttribute('data-mins'), 10);
      if (window.electronAPI) {
        await window.electronAPI.pauseTracking(mins);
      }
    });
  });

  btnPurge.addEventListener('click', async () => {
    if (window.electronAPI) {
      await window.electronAPI.purgeLocalData();
      alert('Local queued telemetry data purged successfully.');
    }
  });
});
