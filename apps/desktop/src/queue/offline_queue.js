const fs = require('fs');
const path = require('path');

class OfflineQueueManager {
  constructor(dataDir = null) {
    this.dataDir = dataDir || path.join(__dirname, '../../data');
    this.queueFilePath = path.join(this.dataDir, 'offline_queue.json');
    this.ensureDirectory();
  }

  ensureDirectory() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
    if (!fs.existsSync(this.queueFilePath)) {
      fs.writeFileSync(this.queueFilePath, JSON.stringify([]), 'utf8');
    }
  }

  getQueue() {
    try {
      const content = fs.readFileSync(this.queueFilePath, 'utf8');
      return JSON.parse(content || '[]');
    } catch (e) {
      return [];
    }
  }

  enqueueEvent(event) {
    const queue = this.getQueue();
    queue.push({
      ...event,
      queued_at: new Date().toISOString()
    });
    fs.writeFileSync(this.queueFilePath, JSON.stringify(queue, null, 2), 'utf8');
    return queue.length;
  }

  clearQueue() {
    fs.writeFileSync(this.queueFilePath, JSON.stringify([]), 'utf8');
  }

  async syncQueue(apiPostCallback, checkHealthCallback) {
    const queue = this.getQueue();
    if (queue.length === 0) {
      return { synced_count: 0, remaining_count: 0, online: true };
    }

    const isOnline = await checkHealthCallback();
    if (!isOnline) {
      return { synced_count: 0, remaining_count: queue.length, online: false };
    }

    let syncedCount = 0;
    const remainingQueue = [];

    for (const event of queue) {
      const success = await apiPostCallback(event);
      if (success) {
        syncedCount++;
      } else {
        remainingQueue.push(event);
      }
    }

    fs.writeFileSync(this.queueFilePath, JSON.stringify(remainingQueue, null, 2), 'utf8');
    return {
      synced_count: syncedCount,
      remaining_count: remainingQueue.length,
      online: true
    };
  }
}

module.exports = OfflineQueueManager;
