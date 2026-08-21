import { sendTelemetryEvent, TelemetryPayload } from './api.js';

let activeDomain: string | null = null;
let tabSwitchCount = 0;
let idleSeconds = 0;
let lastSyncTimestamp = Date.now();

// 0. Ensure canonical tracking_enabled is initialized (defaults to true)
async function initCanonicalTrackingState() {
  try {
    const storage = await chrome.storage.local.get(['tracking_enabled']);
    if (typeof storage.tracking_enabled !== 'boolean') {
      await chrome.storage.local.set({ tracking_enabled: true });
      console.log('[FocusDNA Extension] Initialized CANONICAL tracking_enabled = true');
    } else {
      console.log(`[FocusDNA Extension] Restored CANONICAL tracking_enabled = ${storage.tracking_enabled}`);
    }
  } catch (e) {
    console.warn('[FocusDNA Extension] Failed to init canonical tracking state:', e);
  }
}

initCanonicalTrackingState();

chrome.runtime.onInstalled.addListener(() => {
  initCanonicalTrackingState();
});

chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === 'local' && changes.tracking_enabled) {
    const newVal = changes.tracking_enabled.newValue;
    console.log(`[FocusDNA Extension] CANONICAL tracking_enabled changed to = ${newVal}`);
  }
});

// 1. Listen for active tab activation (Tab Context Switch)
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  tabSwitchCount++;
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    if (tab && tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('chrome-extension://')) {
      const urlObj = new URL(tab.url);
      activeDomain = urlObj.hostname;
    }
  } catch (e) {
    // Ignore internal pages
  }
});

// 2. Listen for tab URL updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab && tab.active && tab.url) {
    try {
      if (!tab.url.startsWith('chrome://') && !tab.url.startsWith('chrome-extension://')) {
        const urlObj = new URL(tab.url);
        activeDomain = urlObj.hostname;
      }
    } catch (e) {
      // Ignore
    }
  }
});

// 3. Listen for idle state changes
try {
  if (chrome.idle) {
    chrome.idle.setDetectionInterval(60);
    chrome.idle.onStateChanged.addListener((newState) => {
      if (newState === 'idle' || newState === 'locked') {
        idleSeconds += 60;
      }
    });
  }
} catch (e) {
  // Ignore
}

// 4. Listen for external and content script messages from FocusDNA Web Application
const handleWebMessage = async (message: any, sender: any, sendResponse: any) => {
  if (!message || typeof message !== 'object') return;

  if (message.type === 'FOCUSDNA_SESSION_START') {
    const updateData: Record<string, any> = {
      active_focus_session_id: message.session_id
    };
    if (message.token) {
      updateData.user_token = message.token;
    }
    await chrome.storage.local.set(updateData);
    console.log(`[FocusDNA Extension] FOCUSDNA_SESSION_START: session_id=${message.session_id}, token_synced=${!!message.token}`);
    // Immediately dispatch telemetry snapshot on session start
    dispatchPeriodTelemetry();
    sendResponse({ status: 'session_synced', session_id: message.session_id });
  } else if (message.type === 'FOCUSDNA_SESSION_END') {
    await chrome.storage.local.remove(['active_focus_session_id']);
    console.log('[FocusDNA Extension] FOCUSDNA_SESSION_END: active focus session cleared.');
    // Dispatch final telemetry snapshot
    dispatchPeriodTelemetry();
    sendResponse({ status: 'session_ended' });
  } else if (message.type === 'FOCUSDNA_AUTH_SYNC') {
    if (message.token) {
      await chrome.storage.local.set({ user_token: message.token });
      console.log('[FocusDNA Extension] FOCUSDNA_AUTH_SYNC: user_token successfully updated.');
    } else {
      await chrome.storage.local.remove(['user_token']);
      console.log('[FocusDNA Extension] FOCUSDNA_AUTH_SYNC: user_token cleared.');
    }
    sendResponse({ status: 'auth_synced' });
  }
};

chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  handleWebMessage(message, sender, sendResponse);
  return true;
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleWebMessage(message, sender, sendResponse);
  return true;
});

// 5. Setup periodic alarm (Every 30 seconds)
try {
  chrome.alarms.create('focusdna_telemetry_alarm', { periodInMinutes: 0.5 });
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'focusdna_telemetry_alarm') {
      dispatchPeriodTelemetry();
    }
  });
} catch (e) {
  // Ignore
}

async function dispatchPeriodTelemetry() {
  const now = Date.now();
  const durationSeconds = Math.max(1, Math.round((now - lastSyncTimestamp) / 1000));
  lastSyncTimestamp = now;

  if (!activeDomain) {
    activeDomain = 'browser.tab';
  }

  const storage = await chrome.storage.local.get(['active_focus_session_id']);

  const payload: TelemetryPayload = {
    website_domain: activeDomain,
    application_name: 'Google Chrome',
    session_duration: durationSeconds,
    browser_switch_count: tabSwitchCount,
    app_switch_count: 0,
    notification_count: 0,
    idle_seconds: idleSeconds,
    typing_activity_level: idleSeconds > 30 ? 'idle' : 'medium',
    device_type: 'browser_extension',
    timestamp: new Date().toISOString(),
    focus_session_id: storage.active_focus_session_id || null
  };

  const success = await sendTelemetryEvent(payload);
  if (success) {
    tabSwitchCount = 0;
    idleSeconds = 0;
  }
}
