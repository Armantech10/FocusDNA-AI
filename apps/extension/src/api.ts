// FocusDNA AI Chrome Extension API Client
// Transmits ONLY high-level metadata (domain name, tab switches, idle seconds, focus_session_id).
// NO passwords, page contents, messages, screenshots, or keystrokes are ever captured or sent.

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
  focus_session_id?: string | null;
}

export function getDefaultApiEndpoint(): string {
  if (typeof location !== 'undefined' && (location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
    return 'http://localhost:8000/api/events';
  }
  return 'https://focus-dna-ai.vercel.app/api/events';
}

export async function sendTelemetryEvent(payload: TelemetryPayload): Promise<boolean> {
  try {
    const storage = await chrome.storage.local.get(['is_tracking_paused', 'api_endpoint', 'user_token', 'active_focus_session_id']);
    
    if (storage.is_tracking_paused) {
      console.log('[FocusDNA Extension] Telemetry skipped: tracking is currently PAUSED.');
      return false;
    }

    const endpoint = storage.api_endpoint || getDefaultApiEndpoint();
    const token = storage.user_token || null;

    if (storage.active_focus_session_id) {
      payload.focus_session_id = storage.active_focus_session_id;
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.warn(`[FocusDNA Extension] Telemetry ingestion HTTP ${response.status}`);
      return false;
    }

    return true;
  } catch (err) {
    console.warn('[FocusDNA Extension] Telemetry server unreachable:', err);
    return false;
  }
}
