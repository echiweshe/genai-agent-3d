import React from 'react';
import { Box, Typography } from '@mui/material';
import SimpleLLMTester from '../SimpleLLMTester';

const LLMTestPage = () => {
  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        LLM Testing
      </Typography>
      
      <Typography variant="body1" paragraph>
        Test the LLM integration by generating text with different models.
      </Typography>
      
      <SimpleLLMTester />
    </Box>
  );
};

export default LLMTestPage;
