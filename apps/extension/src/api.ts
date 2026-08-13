// FocusDNA AI Chrome Extension API Client
// Transmits ONLY high-level metadata (domain name, tab switches, idle seconds).
// NO passwords, page contents, messages, or keystrokes are ever sent.

export interface TelemetryPayload {
  website_domain: string | null;
  application_name: string;
  session_duration: number;
  browser_switch_count: number;
  app_switch_count: number;
  notification_count: number;
  idle_seconds: number;
  typing_activity_level: string;
  device_type: string;
  timestamp: string;
}

export async function sendTelemetryEvent(payload: TelemetryPayload): Promise<boolean> {
  try {
    // Check if tracking is paused in storage
    const storage = await chrome.storage.local.get(['is_tracking_paused', 'api_endpoint', 'user_token']);
    
    if (storage.is_tracking_paused) {
      console.log('[FocusDNA Extension] Telemetry skipped: tracking is currently PAUSED.');
      return false;
    }

    const endpoint = storage.api_endpoint || 'http://localhost:8000/api/events';
    const token = storage.user_token || 'mock_valid_token_user_123';

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.warn(`[FocusDNA Extension] Ingestion status ${response.status}`);
      return false;
    }

    return true;
  } catch (err) {
    console.warn('[FocusDNA Extension] Telemetry server unreachable:', err);
    return false;
  }
}
