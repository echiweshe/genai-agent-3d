
import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import SimpleLLMTester from '../SimpleLLMTester';

/**
 * Page for testing LLM functionality
 */
function LLMTestPage() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          LLM Testing Page
        </Typography>
        <Typography variant="body1" paragraph align="center">
          Use this page to test the LLM functionality
        </Typography>
        
        <SimpleLLMTester />
      </Box>
    </Container>
  );
}

export default LLMTestPage;
