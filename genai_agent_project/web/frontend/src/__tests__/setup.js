/**
 * Setup file for Jest tests
 */

// Mock for window.matchMedia
window.matchMedia = window.matchMedia || function() {
  return {
    matches: false,
    addListener: function() {},
    removeListener: function() {}
  };
};

// Mock for WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = 1; // OPEN
    
    // Call onopen asynchronously
    setTimeout(() => {
      if (this.onopen) {
        this.onopen();
      }
    }, 0);
  }
  
  send(data) {
    // Store the sent data
    this.lastSentData = data;
    
    // Mock a response
    setTimeout(() => {
      if (this.onmessage) {
        const jsonData = JSON.parse(data);
        let response;
        
        if (jsonData.type === 'ping') {
          response = { type: 'pong' };
        } else if (jsonData.type === 'instruction') {
          response = { 
            type: 'result',
            result: {
              status: 'success',
              message: `Processed instruction: ${jsonData.instruction}`,
              steps_executed: 1,
              results: [{
                step: 1,
                description: 'Test step',
                tool: 'test_tool',
                result: {
                  status: 'success',
                  message: 'Test result'
                }
              }]
            }
          };
        } else if (jsonData.type === 'tool') {
          response = {
            type: 'result',
            result: {
              status: 'success',
              message: `Executed tool: ${jsonData.tool_name}`,
              tool: jsonData.tool_name,
              parameters: jsonData.parameters
            }
          };
        } else {
          response = { type: 'error', message: 'Unknown message type' };
        }
        
        this.onmessage({ data: JSON.stringify(response) });
      }
    }, 10);
  }
  
  close() {
    if (this.onclose) {
      this.onclose({ code: 1000, reason: 'Normal closure' });
    }
  }
}

// Replace the global WebSocket with our mock
global.WebSocket = MockWebSocket;
