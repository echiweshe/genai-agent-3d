import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Components
import AppHeader from './components/AppHeader';
import AppSidebar from './components/AppSidebar';
import StatusBar from './components/StatusBar';

// Pages
import HomePage from './components/pages/HomePage';
import InstructionPage from './components/pages/InstructionPage';
import ToolsPage from './components/pages/ToolsPage';
import ModelsPage from './components/pages/ModelsPage';
import ScenePage from './components/pages/ScenePage';
import DiagramsPage from './components/pages/DiagramsPage';
import SettingsPage from './components/pages/SettingsPage';
import BlenderScriptsPage from './components/pages/BlenderScriptsPage';
import SVGToVideoPage from './components/pages/SVGToVideoPage';

// Pages Import (continued)
import LLMTestPage from './components/pages/LLMTestPage';

// Services
import { getStatus } from './services/api';
import websocketService, { WS_STATUS } from './services/websocket';

// Create theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [systemStatus, setSystemStatus] = useState({
    status: 'loading',
    agent: null,
    redis: null,
    version: null,
  });
  const [wsStatus, setWsStatus] = useState(WS_STATUS.CLOSED);
  const [notifications, setNotifications] = useState([]);

  const navigate = useNavigate();
  const location = useLocation();

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    localStorage.setItem('darkMode', !darkMode ? 'true' : 'false');
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Check system status
  const checkStatus = async () => {
    try {
      const status = await getStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Error checking status:', error);
      setSystemStatus({
        status: 'error',
        error: error.message || 'Failed to connect to server',
      });
    }
  };

  // Add notification
  const addNotification = (notification) => {
    const id = Date.now().toString();
    const newNotification = {
      id,
      ...notification,
      timestamp: new Date(),
    };
    
    setNotifications((prev) => [newNotification, ...prev].slice(0, 100));
    
    return id;
  };

  // Remove notification
  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  // Initialize
  useEffect(() => {
    // Load dark mode preference from localStorage
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode) {
      setDarkMode(savedDarkMode === 'true');
    }

    // Check initial status
    checkStatus();

    // Set up status check interval
    const statusInterval = setInterval(checkStatus, 30000);

    // Connect to WebSocket
    websocketService.connect()
      .then(() => {
        addNotification({
          type: 'success',
          message: 'Connected to server',
        });
      })
      .catch((error) => {
        addNotification({
          type: 'error',
          message: `WebSocket connection failed: ${error.message}`,
        });
      });

    // Set up WebSocket status listener
    const removeStatusListener = websocketService.onStatusChange((status) => {
      setWsStatus(status);
      
      if (status === WS_STATUS.OPEN) {
        addNotification({
          type: 'success',
          message: 'WebSocket connected',
        });
      } else if (status === WS_STATUS.CLOSED) {
        addNotification({
          type: 'warning',
          message: 'WebSocket disconnected',
        });
      } else if (status === WS_STATUS.ERROR) {
        addNotification({
          type: 'error',
          message: 'WebSocket error',
        });
      }
    });

    // Listen for result messages
    const removeResultListener = websocketService.onMessage('result', (data) => {
      const result = data.result;
      
      if (result.status === 'success') {
        addNotification({
          type: 'success',
          message: result.message || 'Operation completed successfully',
        });
      } else if (result.status === 'error') {
        addNotification({
          type: 'error',
          message: result.error || 'Operation failed',
        });
      }
    });

    // Listen for status messages
    const removeStatusMessageListener = websocketService.onMessage('status', (data) => {
      addNotification({
        type: data.status === 'processing' ? 'info' : data.status,
        message: data.message || 'Status update',
      });
    });

    // Listen for error messages
    const removeErrorListener = websocketService.onMessage('error', (data) => {
      addNotification({
        type: 'error',
        message: data.message || 'An error occurred',
      });
    });

    // Clean up
    return () => {
      clearInterval(statusInterval);
      removeStatusListener();
      removeResultListener();
      removeStatusMessageListener();
      removeErrorListener();
      websocketService.disconnect();
    };
  }, []);

  return (
    <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <AppHeader 
          toggleDarkMode={toggleDarkMode} 
          darkMode={darkMode}
          toggleSidebar={toggleSidebar}
          notifications={notifications}
          removeNotification={removeNotification}
        />
        
        <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
          <AppSidebar 
            open={sidebarOpen} 
            onClose={() => setSidebarOpen(false)}
            currentPath={location.pathname}
            navigate={navigate}
          />
          
          <Box component="main" sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <Routes>
              <Route path="/" element={<HomePage systemStatus={systemStatus} addNotification={addNotification} />} />
              <Route path="/instruction" element={<InstructionPage addNotification={addNotification} />} />
              <Route path="/tools" element={<ToolsPage addNotification={addNotification} />} />
              <Route path="/models" element={<ModelsPage addNotification={addNotification} />} />
              <Route path="/scene" element={<ScenePage addNotification={addNotification} />} />
              <Route path="/diagrams" element={<DiagramsPage addNotification={addNotification} />} />
              <Route path="/blender-scripts" element={<BlenderScriptsPage addNotification={addNotification} />} />
              <Route path="/svg-to-video" element={<SVGToVideoPage addNotification={addNotification} />} />
              <Route path="/settings" element={<SettingsPage 
                addNotification={addNotification}
                darkMode={darkMode}
                toggleDarkMode={toggleDarkMode}
              />} />
          <Route path="/llm-test" element={<LLMTestPage />} />
            </Routes>
          </Box>
        </Box>
        
        <StatusBar 
          systemStatus={systemStatus}
          wsStatus={wsStatus}
          onRefresh={checkStatus}
        />
      </Box>
    </ThemeProvider>
  );
}

export default App;
