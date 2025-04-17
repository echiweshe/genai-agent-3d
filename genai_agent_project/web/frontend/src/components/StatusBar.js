import React from 'react';
import { Box, Typography, IconButton, Tooltip, useTheme } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import CircularProgress from '@mui/material/CircularProgress';
import { WS_STATUS } from '../services/websocket';

const StatusBar = ({ systemStatus, wsStatus, onRefresh }) => {
  const theme = useTheme();
  
  const getSystemStatusIcon = () => {
    if (systemStatus.status === 'loading') {
      return <CircularProgress size={16} color="inherit" />;
    } else if (systemStatus.status === 'ok') {
      return <CheckCircleIcon fontSize="small" color="success" />;
    } else {
      return <ErrorIcon fontSize="small" color="error" />;
    }
  };
  
  const getWsStatusIcon = () => {
    if (wsStatus === WS_STATUS.OPEN) {
      return <CheckCircleIcon fontSize="small" color="success" />;
    } else if (wsStatus === WS_STATUS.CONNECTING) {
      return <CircularProgress size={16} color="inherit" />;
    } else if (wsStatus === WS_STATUS.CLOSED) {
      return <WarningIcon fontSize="small" color="warning" />;
    } else {
      return <ErrorIcon fontSize="small" color="error" />;
    }
  };
  
  const getWsStatusText = () => {
    if (wsStatus === WS_STATUS.OPEN) {
      return 'Connected';
    } else if (wsStatus === WS_STATUS.CONNECTING) {
      return 'Connecting...';
    } else if (wsStatus === WS_STATUS.CLOSED) {
      return 'Disconnected';
    } else {
      return 'Error';
    }
  };
  
  return (
    <Box 
      sx={{ 
        borderTop: 1, 
        borderColor: 'divider',
        bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'grey.100',
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        px: 2,
        py: 0.5
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Tooltip title="Refresh Status">
          <IconButton size="small" onClick={onRefresh} sx={{ mr: 1 }}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
          {getSystemStatusIcon()}
          <Typography variant="caption" sx={{ ml: 0.5 }}>
            System: {systemStatus.status === 'ok' ? 'Online' : systemStatus.status === 'loading' ? 'Checking...' : 'Offline'}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {getWsStatusIcon()}
          <Typography variant="caption" sx={{ ml: 0.5 }}>
            WebSocket: {getWsStatusText()}
          </Typography>
        </Box>
      </Box>
      
      <Typography variant="caption" color="text.secondary">
        v{systemStatus.version || '0.1.0'}
      </Typography>
    </Box>
  );
};

export default StatusBar;
