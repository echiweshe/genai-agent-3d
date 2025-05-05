import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  useTheme,
  useMediaQuery
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import CodeIcon from '@mui/icons-material/Code';
import BuildIcon from '@mui/icons-material/Build';
import ViewInArIcon from '@mui/icons-material/ViewInAr';
import SceneIcon from '@mui/icons-material/Landscape';
import DiagramIcon from '@mui/icons-material/Schema';
import BlenderIcon from '@mui/icons-material/Animation';
import VideoCameraBackIcon from '@mui/icons-material/VideoCameraBack';
import SettingsIcon from '@mui/icons-material/Settings';
import ChatIcon from '@mui/icons-material/Chat';

const drawerWidth = 240;

const AppSidebar = ({ open, onClose, currentPath, navigate }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, path: '/' },
    { text: 'Instructions', icon: <CodeIcon />, path: '/instruction' },
    { text: 'Tools', icon: <BuildIcon />, path: '/tools' },
    { text: 'Models', icon: <ViewInArIcon />, path: '/models' },
    { text: 'Scene Editor', icon: <SceneIcon />, path: '/scene' },
    { text: 'Diagrams', icon: <DiagramIcon />, path: '/diagrams' },
    { text: 'Blender Scripts', icon: <BlenderIcon />, path: '/blender-scripts' },
    { text: 'SVG to Video', icon: <VideoCameraBackIcon />, path: '/svg-to-video' },
    { text: 'LLM Test', icon: <ChatIcon />, path: '/llm-test' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];
  
  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };
  
  const drawer = (
    <Box sx={{ pt: 1 }}>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              selected={currentPath === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ mt: 2 }} />
      
      <Box sx={{ p: 2, mt: 2 }}>
        <img 
          src="/logo192.png" 
          alt="GenAI Agent 3D" 
          style={{ 
            width: '100%', 
            maxWidth: 100, 
            display: 'block',
            margin: '0 auto'
          }} 
        />
      </Box>
    </Box>
  );
  
  return (
    <>
      {/* Mobile drawer */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={open}
          onClose={onClose}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth 
            },
          }}
        >
          {drawer}
        </Drawer>
      )}
      
      {/* Desktop drawer */}
      {!isMobile && (
        <Drawer
          variant="persistent"
          open={open}
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              position: 'relative',
              height: '100%',
              border: 'none'
            },
            width: open ? drawerWidth : 0,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }}
        >
          {drawer}
        </Drawer>
      )}
    </>
  );
};

export default AppSidebar;
