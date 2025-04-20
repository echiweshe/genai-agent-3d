import { apiUrl } from './api';

/**
 * Service for interacting with the Blender script execution API
 */
const blenderScriptService = {
  /**
   * List available Blender scripts in a folder
   * 
   * @param {string} folder - The folder to list scripts from (e.g., 'models', 'scenes')
   * @returns {Promise<Object>} - A promise that resolves to the API response
   */
  listScripts: async (folder = '') => {
    try {
      console.log(`Service: Listing scripts in folder: ${folder}`);
      console.log(`Service: Making request to: ${apiUrl}/blender/list-scripts/${folder}`);
      
      const response = await fetch(`${apiUrl}/blender/list-scripts/${folder}`);
      
      console.log(`Service: Response status: ${response.status}`);
      
      const responseText = await response.text();
      console.log(`Service: Response body (first 200 chars): ${responseText.substring(0, 200)}`);
      
      let data;
      try {
        data = JSON.parse(responseText);
      } catch (parseError) {
        console.error('Service: Failed to parse JSON response:', parseError);
        console.error('Service: Response text:', responseText);
        throw new Error(`Invalid JSON response: ${responseText.substring(0, 100)}...`);
      }
      
      if (!response.ok) {
        console.error('Service: Error response:', data);
        throw new Error(data.detail || `Server error (${response.status})`);
      }
      
      return data;
    } catch (error) {
      console.error('Service: Error listing scripts:', error);
      throw error;
    }
  },

  /**
   * Execute a Blender script
   * 
   * @param {string} scriptPath - The path to the script to execute
   * @param {boolean} showUI - Whether to show the Blender UI
   * @returns {Promise<Object>} - A promise that resolves to the API response
   */
  executeScript: async (scriptPath, showUI = false) => {
    try {
      const response = await fetch(`${apiUrl}/blender/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script_path: scriptPath,
          show_ui: showUI
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to execute script');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error executing script:', error);
      throw error;
    }
  },

  /**
   * Get the status of a Blender script execution
   * 
   * @param {string} executionId - The ID of the execution to check
   * @returns {Promise<Object>} - A promise that resolves to the API response
   */
  getStatus: async (executionId) => {
    try {
      const response = await fetch(`${apiUrl}/blender/status/${executionId}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get script status');
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting script status:', error);
      throw error;
    }
  },

  /**
   * Get the output of a Blender script execution
   * 
   * @param {string} executionId - The ID of the execution to get output for
   * @returns {Promise<Object>} - A promise that resolves to the API response
   */
  getOutput: async (executionId) => {
    try {
      const response = await fetch(`${apiUrl}/blender/output/${executionId}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get script output');
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting script output:', error);
      throw error;
    }
  },

  /**
   * Create a WebSocket connection for a Blender script execution
   * 
   * @param {string} executionId - The ID of the execution to connect to
   * @returns {WebSocket} - A WebSocket connection
   */
  createWebSocketConnection: (executionId) => {
    const wsUrl = apiUrl.replace('http', 'ws');
    const ws = new WebSocket(`${wsUrl}/ws/blender/${executionId}`);
    return ws;
  }
};

export default blenderScriptService;
