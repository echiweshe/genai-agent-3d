import React, { useState } from 'react';
import { Container, Typography, Box, Paper, Tabs, Tab, Button } from '@mui/material';
import BlenderScriptViewer from '../viewers/BlenderScriptViewer';
import BlenderDebugHelper from '../debug/BlenderDebugHelper';

/**
 * BlenderScriptsPage - Page for managing and executing Blender scripts
 * 
 * This page allows users to browse, view, and execute Blender scripts
 * It provides tabs for different script categories (models, scenes, etc.)
 */
const BlenderScriptsPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedScript, setSelectedScript] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleScriptSelected = (scriptPath) => {
    setSelectedScript(scriptPath);
  };

  // Define the folders for each tab
  const tabFolders = ['models', 'scenes', 'diagrams', 'tools'];

  return (
    <Container maxWidth="xl">
      <Box my={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h4" component="h1">
            Blender Scripts
          </Typography>
          <BlenderDebugHelper />
        </Box>
        
        <Typography variant="subtitle1" gutterBottom>
          Browse, view, and execute Blender scripts generated by GenAI Agent 3D
        </Typography>
        
        <Paper elevation={2} sx={{ mb: 4 }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            indicatorColor="primary"
            textColor="primary"
            variant="scrollable"
            scrollButtons="auto"
          >
            {tabFolders.map((folder, index) => (
              <Tab key={index} label={folder.charAt(0).toUpperCase() + folder.slice(1)} />
            ))}
          </Tabs>
        </Paper>
        
        <Box mt={3}>
          <BlenderScriptViewer 
            scriptPath={selectedScript}
            onScriptSelected={handleScriptSelected}
            folder={tabFolders[activeTab]}
          />
        </Box>
      </Box>
    </Container>
  );
};

export default BlenderScriptsPage;
