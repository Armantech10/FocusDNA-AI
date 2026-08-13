document.addEventListener('DOMContentLoaded', async () => {
  const apiEndpointEl = document.getElementById('apiEndpoint') as HTMLInputElement;
  const userTokenEl = document.getElementById('userToken') as HTMLInputElement;
  const saveBtn = document.getElementById('saveBtn');
  const savedMsg = document.getElementById('savedMsg');

  // Load existing options
  const storage = await chrome.storage.local.get(['api_endpoint', 'user_token']);
  if (storage.api_endpoint && apiEndpointEl) {
    apiEndpointEl.value = storage.api_endpoint;
  }
  if (storage.user_token && userTokenEl) {
    userTokenEl.value = storage.user_token;
  }

  saveBtn?.addEventListener('click', async () => {
    const endpoint = apiEndpointEl?.value.trim() || 'http://localhost:8000/api/events';
    const token = userTokenEl?.value.trim() || 'mock_valid_token_user_123';

    await chrome.storage.local.set({
      api_endpoint: endpoint,
      user_token: token
    });

    if (savedMsg) {
      savedMsg.style.display = 'inline';
      setTimeout(() => {
        savedMsg.style.display = 'none';
      }, 2500);
    }
  });
});
