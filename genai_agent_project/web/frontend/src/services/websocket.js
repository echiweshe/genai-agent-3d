/**
 * WebSocket Service for real-time communication with the backend
 */

// WebSocket connection status
const WS_STATUS = {
  CONNECTING: 'connecting',
  OPEN: 'open',
  CLOSED: 'closed',
  ERROR: 'error',
};

class WebSocketService {
  constructor() {
    this.socket = null;
    this.status = WS_STATUS.CLOSED;
    this.listeners = new Map();
    this.reconnectTimer = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 2000; // 2 seconds
    this.pingInterval = null;
    this.url = null;
  }

  /**
   * Connect to the WebSocket server
   * @param {string} url - WebSocket server URL
   * @returns {Promise} Promise that resolves when connected
   */
  connect(url = 'ws://localhost:8000/ws') {
    return new Promise((resolve, reject) => {
      if (this.socket && this.status === WS_STATUS.OPEN) {
        resolve();
        return;
      }

      this.url = url;
      this.status = WS_STATUS.CONNECTING;
      this._notifyStatusListeners();

      try {
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.status = WS_STATUS.OPEN;
          this._notifyStatusListeners();
          this.reconnectAttempts = 0;
          this._startPingInterval();
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this._notifyMessageListeners(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.socket.onclose = () => {
          console.log('WebSocket disconnected');
          this.status = WS_STATUS.CLOSED;
          this._notifyStatusListeners();
          this._stopPingInterval();
          this._scheduleReconnect();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.status = WS_STATUS.ERROR;
          this._notifyStatusListeners();
          reject(error);
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        this.status = WS_STATUS.ERROR;
        this._notifyStatusListeners();
        reject(error);
      }
    });
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.status = WS_STATUS.CLOSED;
      this._notifyStatusListeners();
      this._stopPingInterval();
      this._clearReconnect();
    }
  }

  /**
   * Send a message to the server
   * @param {Object} message - Message to send
   * @returns {boolean} Whether the message was sent
   */
  send(message) {
    if (this.socket && this.status === WS_STATUS.OPEN) {
      try {
        this.socket.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        return false;
      }
    }
    return false;
  }

  /**
   * Add a listener for status changes
   * @param {Function} listener - Listener function
   * @returns {Function} Function to remove the listener
   */
  onStatusChange(listener) {
    if (!this.listeners.has('status')) {
      this.listeners.set('status', []);
    }

    const statusListeners = this.listeners.get('status');
    statusListeners.push(listener);

    // Return a function to remove the listener
    return () => {
      const index = statusListeners.indexOf(listener);
      if (index !== -1) {
        statusListeners.splice(index, 1);
      }
    };
  }

  /**
   * Add a listener for messages
   * @param {string} type - Message type to listen for
   * @param {Function} listener - Listener function
   * @returns {Function} Function to remove the listener
   */
  onMessage(type, listener) {
    const key = `message:${type}`;

    if (!this.listeners.has(key)) {
      this.listeners.set(key, []);
    }

    const messageListeners = this.listeners.get(key);
    messageListeners.push(listener);

    // Return a function to remove the listener
    return () => {
      const index = messageListeners.indexOf(listener);
      if (index !== -1) {
        messageListeners.splice(index, 1);
      }
    };
  }

  /**
   * Get the current connection status
   * @returns {string} Current status
   */
  getStatus() {
    return this.status;
  }

  /**
   * Send a ping to keep the connection alive
   */
  _ping() {
    this.send({ type: 'ping' });
  }

  /**
   * Start the ping interval
   */
  _startPingInterval() {
    this._stopPingInterval();
    this.pingInterval = setInterval(() => this._ping(), 30000); // 30 seconds
  }

  /**
   * Stop the ping interval
   */
  _stopPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Schedule a reconnection attempt
   */
  _scheduleReconnect() {
    this._clearReconnect();

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      console.log(`Scheduling reconnect attempt ${this.reconnectAttempts + 1} in ${this.reconnectInterval}ms`);
      this.reconnectTimer = setTimeout(() => {
        this.reconnectAttempts++;
        this.connect(this.url).catch(() => {
          // If reconnect fails, it will trigger onclose which will schedule another reconnect
        });
      }, this.reconnectInterval);
    } else {
      console.log('Max reconnect attempts reached');
    }
  }

  /**
   * Clear reconnection timer
   */
  _clearReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Notify status listeners of a status change
   */
  _notifyStatusListeners() {
    if (this.listeners.has('status')) {
      const statusListeners = this.listeners.get('status');
      statusListeners.forEach((listener) => {
        try {
          listener(this.status);
        } catch (error) {
          console.error('Error in status listener:', error);
        }
      });
    }
  }

  /**
   * Notify message listeners of a received message
   * @param {Object} data - Message data
   */
  _notifyMessageListeners(data) {
    const type = data.type;
    if (!type) {
      return;
    }

    const key = `message:${type}`;

    // Notify type-specific listeners
    if (this.listeners.has(key)) {
      const messageListeners = this.listeners.get(key);
      messageListeners.forEach((listener) => {
        try {
          listener(data);
        } catch (error) {
          console.error(`Error in message listener for type ${type}:`, error);
        }
      });
    }

    // Notify all-message listeners
    if (this.listeners.has('message:*')) {
      const allMessageListeners = this.listeners.get('message:*');
      allMessageListeners.forEach((listener) => {
        try {
          listener(data);
        } catch (error) {
          console.error('Error in all-message listener:', error);
        }
      });
    }
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export default websocketService;
export { WS_STATUS };
