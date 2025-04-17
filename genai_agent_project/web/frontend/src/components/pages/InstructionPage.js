import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  CircularProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import { processInstruction } from '../../services/api';
import websocketService from '../../services/websocket';

const InstructionPage = ({ addNotification }) => {
  const [instruction, setInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!instruction.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please enter an instruction',
      });
      return;
    }
    
    try {
      setLoading(true);
      
      // Add the instruction to results
      const timestamp = new Date();
      const instructionId = `instruction-${timestamp.getTime()}`;
      
      setResults(prev => [...prev, {
        id: instructionId,
        type: 'instruction',
        content: instruction,
        timestamp,
      }]);
      
      // Try to use WebSockets for real-time updates
      const wsAvailable = websocketService.getStatus() === 'open';
      
      if (wsAvailable) {
        // Send instruction via WebSocket
        websocketService.send({
          type: 'instruction',
          instruction,
          context: {},
        });
        
        // Listen for the result
        const resultListener = (data) => {
          if (data.type === 'result') {
            // Add result to the results list
            setResults(prev => [...prev, {
              id: `result-${new Date().getTime()}`,
              type: 'result',
              content: data.result,
              timestamp: new Date(),
              instructionId,
            }]);
            
            // Remove the listener
            removeResultListener();
            setLoading(false);
          }
        };
        
        // Add listener
        const removeResultListener = websocketService.onMessage('result', resultListener);
      } else {
        // Fallback to REST API
        const result = await processInstruction(instruction);
        
        // Add result to the results list
        setResults(prev => [...prev, {
          id: `result-${new Date().getTime()}`,
          type: 'result',
          content: result,
          timestamp: new Date(),
          instructionId,
        }]);
        
        setLoading(false);
      }
      
      // Clear the instruction
      setInstruction('');
      
    } catch (error) {
      setLoading(false);
      
      // Add error to the results list
      setResults(prev => [...prev, {
        id: `error-${new Date().getTime()}`,
        type: 'error',
        content: error.message || 'An error occurred',
        timestamp: new Date(),
      }]);
      
      addNotification({
        type: 'error',
        message: `Error processing instruction: ${error.message}`,
      });
    }
  };
  
  const renderStepResult = (step) => {
    if (!step.result) return null;
    
    const status = step.result.status;
    const color = status === 'success' ? 'success' : status === 'error' ? 'error' : 'default';
    
    return (
      <Box sx={{ mt: 1 }}>
        <Chip 
          label={status} 
          color={color} 
          size="small" 
          sx={{ mb: 1 }}
        />
        <Typography variant="body2" component="pre" sx={{ 
          whiteSpace: 'pre-wrap',
          bgcolor: 'background.paper',
          p: 1,
          borderRadius: 1,
          fontSize: '0.875rem',
          overflow: 'auto',
          maxHeight: 300,
        }}>
          {JSON.stringify(step.result, null, 2)}
        </Typography>
      </Box>
    );
  };
  
  const renderResult = (item) => {
    if (item.type === 'instruction') {
      return (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            {item.timestamp.toLocaleString()}
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
            <Typography variant="body1">
              {item.content}
            </Typography>
          </Paper>
        </Box>
      );
    } else if (item.type === 'result') {
      const result = item.content;
      
      return (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            {item.timestamp.toLocaleString()}
          </Typography>
          
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6">
                Result
              </Typography>
              <Chip 
                label={result.status} 
                color={result.status === 'success' ? 'success' : result.status === 'error' ? 'error' : 'default'} 
                size="small" 
              />
            </Box>
            
            {result.error && (
              <Typography color="error" sx={{ mb: 1 }}>
                {result.error}
              </Typography>
            )}
            
            {result.message && (
              <Typography sx={{ mb: 1 }}>
                {result.message}
              </Typography>
            )}
            
            {result.steps_executed > 0 && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="subtitle1">
                  Steps Executed: {result.steps_executed}
                </Typography>
                
                {result.results && result.results.map((step, index) => (
                  <Accordion key={index} sx={{ mt: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>
                        Step {step.step}: {step.description}
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Tool: {step.tool}
                      </Typography>
                      {renderStepResult(step)}
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}
          </Paper>
        </Box>
      );
    } else if (item.type === 'error') {
      return (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            {item.timestamp.toLocaleString()}
          </Typography>
          <Paper sx={{ p: 2, bgcolor: 'error.light', color: 'error.contrastText' }}>
            <Typography variant="body1">
              Error: {item.content}
            </Typography>
          </Paper>
        </Box>
      );
    }
    
    return null;
  };
  
  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        Instructions
      </Typography>
      
      <Typography variant="body1" paragraph>
        Enter natural language instructions for the agent to process.
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            label="Enter your instruction"
            multiline
            rows={4}
            fullWidth
            variant="outlined"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="e.g., Create a scene with a red cube on a blue plane"
            disabled={loading}
          />
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
              type="submit"
              disabled={loading || !instruction.trim()}
            >
              {loading ? 'Processing...' : 'Send Instruction'}
            </Button>
          </Box>
        </form>
      </Paper>
      
      <Typography variant="h6" gutterBottom>
        Results
      </Typography>
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {results.length === 0 ? (
          <Typography color="text.secondary">
            No results yet. Enter an instruction to get started.
          </Typography>
        ) : (
          <Box>
            {results.map(item => (
              <Box key={item.id}>
                {renderResult(item)}
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default InstructionPage;
