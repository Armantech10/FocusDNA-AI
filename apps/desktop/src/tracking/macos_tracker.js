const { execSync } = require('child_process');

class MacosTracker {
  constructor() {
    this.platform = 'darwin';
  }

  /**
   * Retrieves the currently active foreground application name on macOS.
   * Metadata ONLY: App name string (e.g., "Xcode", "Visual Studio Code", "Safari").
   * NEVER collects keystrokes, passwords, message text, or screenshots.
   */
  getActiveApplication() {
    try {
      const script = `
        tell application "System Events"
          set frontApp to name of first application process whose frontmost is true
          return frontApp
        end tell
      `;
      const output = execSync(`osascript -e '${script}'`, { timeout: 1500, encoding: 'utf8' });
      return output.trim() || 'Finder';
    } catch (error) {
      return 'Desktop';
    }
  }

  /**
   * Reads macOS system idle duration in seconds via ioreg HIDIdleTime.
   */
  getIdleTimeSeconds() {
    try {
      const output = execSync('ioreg -c IOHIDSystem | grep HIDIdleTime', { timeout: 1500, encoding: 'utf8' });
      const match = output.match(/HIDIdleTime"\s*=\s*(\d+)/);
      if (match && match[1]) {
        const nanoseconds = parseInt(match[1], 10);
        return Math.floor(nanoseconds / 1000000000);
      }
      return 0;
    } catch (error) {
      return 0;
    }
  }
}

module.exports = MacosTracker;
