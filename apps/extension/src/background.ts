import { sendTelemetryEvent, TelemetryPayload } from './api.js';

let activeDomain: string | null = null;
let tabSwitchCount = 0;
let idleSeconds = 0;
let lastSyncTimestamp = Date.now();

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

// 4. Setup periodic alarm (Every 30 seconds)
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
    timestamp: new Date().toISOString()
  };

  const success = await sendTelemetryEvent(payload);
  if (success) {
    tabSwitchCount = 0;
    idleSeconds = 0;
  }
}
