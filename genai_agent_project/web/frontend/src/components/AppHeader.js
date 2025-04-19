import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton, 
  Menu,
  MenuItem,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Box
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import NotificationsIcon from '@mui/icons-material/Notifications';
import CloseIcon from '@mui/icons-material/Close';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';

const AppHeader = ({ toggleDarkMode, darkMode, toggleSidebar, notifications, removeNotification, setNotifications }) => {
  const [notificationMenuAnchor, setNotificationMenuAnchor] = useState(null);
  const [notificationsDrawerOpen, setNotificationsDrawerOpen] = useState(false);
  
  const handleNotificationMenuOpen = (event) => {
    setNotificationMenuAnchor(event.currentTarget);
  };
  
  const handleNotificationMenuClose = () => {
    setNotificationMenuAnchor(null);
  };
  
  const openNotificationsDrawer = () => {
    handleNotificationMenuClose();
    setNotificationsDrawerOpen(true);
  };
  
  const closeNotificationsDrawer = () => {
    setNotificationsDrawerOpen(false);
  };
  
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'info':
        return <InfoIcon color="info" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };
  
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={toggleSidebar}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            GenAI Agent 3D
          </Typography>
          
          <IconButton
            size="large"
            color="inherit"
            onClick={toggleDarkMode}
            aria-label="toggle dark mode"
          >
            {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          
          <IconButton
            size="large"
            color="inherit"
            onClick={handleNotificationMenuOpen}
            aria-label="notifications"
          >
            <Badge badgeContent={notifications.length} color="secondary">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          
          <Menu
            anchorEl={notificationMenuAnchor}
            open={Boolean(notificationMenuAnchor)}
            onClose={handleNotificationMenuClose}
          >
            <MenuItem onClick={openNotificationsDrawer}>View all notifications</MenuItem>
            <MenuItem onClick={() => {
              setNotifications([]);
              handleNotificationMenuClose();
            }}>
              Clear all notifications
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Drawer
        anchor="right"
        open={notificationsDrawerOpen}
        onClose={closeNotificationsDrawer}
      >
        <Box sx={{ width: 350, pt: 1, height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ px: 2, pb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Notifications</Typography>
            <IconButton onClick={closeNotificationsDrawer}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Divider />
          
          {notifications.length === 0 ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography color="textSecondary">No notifications</Typography>
            </Box>
          ) : (
            <List sx={{ overflowY: 'auto', flexGrow: 1 }}>
              {notifications.map((notification) => (
                <ListItem 
                  key={notification.id}
                  secondaryAction={
                    <IconButton edge="end" onClick={() => removeNotification(notification.id)}>
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  }
                >
                  <ListItemIcon>
                    {getNotificationIcon(notification.type)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={notification.message}
                    secondary={notification.timestamp.toLocaleTimeString()}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Drawer>
    </>
  );
};

export default AppHeader;
