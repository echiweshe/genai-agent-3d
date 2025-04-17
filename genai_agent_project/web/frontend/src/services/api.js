/**
 * API Service for communicating with the backend
 */

import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get system status
 * @returns {Promise} Promise with system status
 */
export const getStatus = async () => {
  try {
    const response = await api.get('/status');
    return response.data;
  } catch (error) {
    console.error('Error getting status:', error);
    throw error;
  }
};

/**
 * Process an instruction
 * @param {string} instruction - The instruction to process
 * @param {Object} context - Optional context for the instruction
 * @returns {Promise} Promise with instruction result
 */
export const processInstruction = async (instruction, context = {}) => {
  try {
    const response = await api.post('/instruction', {
      instruction,
      context,
    });
    return response.data;
  } catch (error) {
    console.error('Error processing instruction:', error);
    throw error;
  }
};

/**
 * Execute a specific tool
 * @param {string} toolName - The name of the tool to execute
 * @param {Object} parameters - Tool parameters
 * @returns {Promise} Promise with tool execution result
 */
export const executeTool = async (toolName, parameters = {}) => {
  try {
    const response = await api.post('/tool', {
      tool_name: toolName,
      parameters,
    });
    return response.data;
  } catch (error) {
    console.error('Error executing tool:', error);
    throw error;
  }
};

/**
 * Get available tools
 * @returns {Promise} Promise with available tools
 */
export const getTools = async () => {
  try {
    const response = await api.get('/tools');
    return response.data;
  } catch (error) {
    console.error('Error getting tools:', error);
    throw error;
  }
};

/**
 * Get system configuration
 * @returns {Promise} Promise with system configuration
 */
export const getConfig = async () => {
  try {
    const response = await api.get('/config');
    return response.data;
  } catch (error) {
    console.error('Error getting configuration:', error);
    throw error;
  }
};

/**
 * Update system configuration
 * @param {string} section - Configuration section
 * @param {string} key - Configuration key
 * @param {any} value - New value
 * @returns {Promise} Promise with update result
 */
export const updateConfig = async (section, key, value) => {
  try {
    const response = await api.post('/config', {
      section,
      key,
      value,
    });
    return response.data;
  } catch (error) {
    console.error('Error updating configuration:', error);
    throw error;
  }
};

/**
 * Upload a file
 * @param {File} file - The file to upload
 * @returns {Promise} Promise with upload result
 */
export const uploadFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

/**
 * Get the URL for a result file
 * @param {string} filename - The filename
 * @returns {string} The URL for the file
 */
export const getResultFileUrl = (filename) => {
  return `${api.defaults.baseURL}/results/${filename}`;
};

export default {
  getStatus,
  processInstruction,
  executeTool,
  getTools,
  getConfig,
  updateConfig,
  uploadFile,
  getResultFileUrl,
};
