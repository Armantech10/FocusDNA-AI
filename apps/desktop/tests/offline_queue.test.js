const assert = require('assert');
const fs = require('fs');
const path = require('path');
const OfflineQueueManager = require('../src/queue/offline_queue');

async function testOfflineQueue() {
  console.log('[Desktop Unit Test] Running Offline Queue Manager Verification...');

  const testDir = path.join(__dirname, 'temp_queue_data');
  const queueMgr = new OfflineQueueManager(testDir);

  // 1. Initial State Check
  queueMgr.clearQueue();
  assert.strictEqual(queueMgr.getQueue().length, 0, 'Initial queue should be empty');

  // 2. Enqueue Telemetry Event
  const mockEvent = {
    application_name: 'Visual Studio Code',
    duration: 300,
    app_switch_count: 2,
    idle_seconds: 10,
    timestamp: new Date().toISOString()
  };

  const count = queueMgr.enqueueEvent(mockEvent);
  assert.strictEqual(count, 1, 'Queue count should be 1 after enqueuing');

  // 3. Privacy Safeguard Audit (Verify zero prohibited fields)
  const item = queueMgr.getQueue()[0];
  assert.strictEqual(item.application_name, 'Visual Studio Code');
  assert.strictEqual(item.keystrokes, undefined, 'Keystrokes MUST be undefined');
  assert.strictEqual(item.passwords, undefined, 'Passwords MUST be undefined');
  assert.strictEqual(item.screenshots, undefined, 'Screenshots MUST be undefined');

  // 4. Test Sync Handler (Online case)
  const result = await queueMgr.syncQueue(
    async (evt) => true, // Mock successful API post
    async () => true    // Mock backend health OK
  );

  assert.strictEqual(result.synced_count, 1, 'Should sync 1 item');
  assert.strictEqual(result.remaining_count, 0, 'Remaining queue should be 0');
  assert.strictEqual(queueMgr.getQueue().length, 0, 'Queue file should be empty after sync');

  // Cleanup test directory
  try {
    fs.rmSync(testDir, { recursive: true, force: true });
  } catch (e) {}

  console.log('✅ [Desktop Unit Test] Offline Queue Manager test passed 100%!');
}

testOfflineQueue().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
