import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, CircularProgress, Tabs, Tab } from '@mui/material';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { vs2015 } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { Editor } from '@monaco-editor/react';
import ModelViewer from './ModelViewer';
import DiagramViewer from './DiagramViewer';

// Helper to get file extension
const getFileExtension = (filename) => {
  return filename?.split('.').pop()?.toLowerCase() || '';
};

// Helper to determine syntax highlighting language based on file extension
const getSyntaxLanguage = (extension) => {
  const languageMap = {
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    py: 'python',
    html: 'html',
    css: 'css',
    json: 'json',
    xml: 'xml',
    md: 'markdown',
    txt: 'text',
    sh: 'bash',
    cpp: 'cpp',
    c: 'c',
    h: 'cpp',
    java: 'java',
    cs: 'csharp',
    sql: 'sql',
    php: 'php',
    rb: 'ruby',
    go: 'go',
    rs: 'rust',
    swift: 'swift',
    kt: 'kotlin',
    pl: 'perl',
    yaml: 'yaml',
    yml: 'yaml',
    graphql: 'graphql',
    scala: 'scala',
    groovy: 'groovy',
    dart: 'dart',
    lua: 'lua',
    r: 'r',
    m: 'objectivec',
    mm: 'objectivec',
  };
  
  return languageMap[extension] || 'text';
};

// Helper to determine file type category
const getFileType = (fileUrl, fileExtension) => {
  // Get extension from URL if not provided
  const extension = fileExtension || getFileExtension(fileUrl);
  
  // 3D model files
  if (['gltf', 'glb', 'obj', 'stl', 'ply', 'fbx', '3ds', 'blend'].includes(extension)) {
    return '3d';
  }
  
  // Image files
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(extension)) {
    return 'image';
  }
  
  // Diagram files
  if (['mmd', 'dot'].includes(extension) || fileUrl?.includes('diagram') || fileUrl?.includes('mermaid')) {
    return 'diagram';
  }
  
  // Text and code files
  if (['txt', 'md', 'js', 'jsx', 'ts', 'tsx', 'py', 'java', 'html', 'css', 'json', 'xml', 
       'c', 'cpp', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'sh', 'sql', 'yaml', 'yml'].includes(extension)) {
    return 'code';
  }
  
  // PDF files
  if (['pdf'].includes(extension)) {
    return 'pdf';
  }
  
  // Audio files
  if (['mp3', 'wav', 'ogg', 'flac', 'm4a'].includes(extension)) {
    return 'audio';
  }
  
  // Video files
  if (['mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'].includes(extension)) {
    return 'video';
  }
  
  // Default to binary if unknown
  return 'binary';
};

const FileViewer = ({ fileUrl, fileContent, fileName, fileType, width = '100%', height = '500px' }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [content, setContent] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Determine file type if not provided
  const extension = getFileExtension(fileName || fileUrl);
  const detectedFileType = fileType || getFileType(fileUrl, extension);
  
  useEffect(() => {
    const loadContent = async () => {
      // Reset state
      setLoading(true);
      setError(null);
      setContent(null);
      
      try {
        // If content is directly provided, use that
        if (fileContent) {
          setContent(fileContent);
          setLoading(false);
          return;
        }
        
        // If no URL is provided, show an error
        if (!fileUrl) {
          throw new Error('No file URL or content provided');
        }
        
        // Fetch the content from URL
        const response = await fetch(fileUrl);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch file: ${response.statusText}`);
        }
        
        // Handle different file types
        if (detectedFileType === 'code' || detectedFileType === 'diagram') {
          // Get text content for code and diagrams
          const text = await response.text();
          setContent(text);
        } else if (detectedFileType === '3d' || detectedFileType === 'image' || 
                  detectedFileType === 'video' || detectedFileType === 'audio' || 
                  detectedFileType === 'pdf') {
          // Just use the URL for binary files that can be displayed directly
          setContent(fileUrl);
        } else {
          // For binary files, just use the URL
          setContent(fileUrl);
        }
      } catch (err) {
        console.error('Error loading file:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    loadContent();
  }, [fileUrl, fileContent, detectedFileType]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Render loading state
  if (loading) {
    return (
      <Box 
        sx={{ 
          width, 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bgcolor: 'background.paper',
          borderRadius: 1,
        }}
      >
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading file...
        </Typography>
      </Box>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <Paper 
        elevation={3}
        sx={{ 
          width, 
          height, 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Typography variant="h6" color="error" gutterBottom>
          Error Loading File
        </Typography>
        <Typography variant="body1">
          {error}
        </Typography>
      </Paper>
    );
  }
  
  // Render empty state
  if (!content) {
    return (
      <Paper 
        elevation={3}
        sx={{ 
          width, 
          height, 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Typography variant="h6" gutterBottom>
          No File Selected
        </Typography>
        <Typography variant="body1">
          Please select a file to view
        </Typography>
      </Paper>
    );
  }
  
  // Render file based on type
  const renderFileContent = () => {
    switch (detectedFileType) {
      case '3d':
        return <ModelViewer modelUrl={content} modelType={extension} width="100%" height="100%" />;
        
      case 'image':
        return (
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              height: '100%',
              overflow: 'auto',
            }}
          >
            <img 
              src={content} 
              alt={fileName || 'Image'} 
              style={{ 
                maxWidth: '100%', 
                maxHeight: '100%', 
                objectFit: 'contain' 
              }} 
            />
          </Box>
        );
        
      case 'diagram':
        return <DiagramViewer diagramCode={content} diagramType={extension === 'dot' ? 'dot' : 'mermaid'} width="100%" height="100%" />;
        
      case 'video':
        return (
          <Box 
            sx={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              height: '100%'
            }}
          >
            <video 
              controls 
              src={content} 
              style={{ maxWidth: '100%', maxHeight: '100%' }}
            >
              Your browser does not support the video tag.
            </video>
          </Box>
        );
        
      case 'audio':
        return (
          <Box 
            sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              justifyContent: 'center', 
              alignItems: 'center',
              height: '100%',
              p: 3,
            }}
          >
            <Typography variant="h6" gutterBottom>
              {fileName || 'Audio'}
            </Typography>
            <audio controls src={content} style={{ width: '100%' }}>
              Your browser does not support the audio element.
            </audio>
          </Box>
        );
        
      case 'pdf':
        return (
          <Box sx={{ height: '100%', width: '100%' }}>
            <iframe 
              src={`${content}#view=FitH`} 
              title={fileName || 'PDF Document'} 
              width="100%" 
              height="100%" 
              style={{ border: 'none' }}
            >
              This browser does not support PDFs. Please download the PDF to view it.
            </iframe>
          </Box>
        );
        
      case 'code':
        // For code files, show both the editor and syntax highlighter with tabs
        return (
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="code viewer tabs">
              <Tab label="Editor" />
              <Tab label="Viewer" />
            </Tabs>
            
            <Box sx={{ flexGrow: 1, display: tabValue === 0 ? 'block' : 'none', height: 0 }}>
              <Editor
                height="100%"
                defaultLanguage={getSyntaxLanguage(extension)}
                defaultValue={content}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: true },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                }}
              />
            </Box>
            
            <Box 
              sx={{ 
                flexGrow: 1, 
                display: tabValue === 1 ? 'block' : 'none',
                height: 0,
                overflow: 'auto',
              }}
            >
              <SyntaxHighlighter
                language={getSyntaxLanguage(extension)}
                style={vs2015}
                showLineNumbers
                customStyle={{
                  margin: 0,
                  padding: '16px',
                  height: '100%',
                  overflow: 'auto',
                }}
              >
                {content}
              </SyntaxHighlighter>
            </Box>
          </Box>
        );
        
      default:
        // For binary or unknown files, show download link
        return (
          <Box 
            sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              justifyContent: 'center', 
              alignItems: 'center',
              height: '100%',
              p: 3,
            }}
          >
            <Typography variant="h6" gutterBottom>
              Binary File
            </Typography>
            <Typography variant="body1" gutterBottom>
              This file type cannot be previewed directly.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              File: {fileName || fileUrl.split('/').pop()}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <a 
                href={content} 
                download={fileName || 'download'}
                style={{ 
                  color: 'inherit',
                  textDecoration: 'none',
                }}
              >
                <Paper 
                  elevation={2} 
                  sx={{ 
                    px: 3, 
                    py: 1, 
                    bgcolor: 'primary.main', 
                    color: 'primary.contrastText',
                    '&:hover': { bgcolor: 'primary.dark' },
                  }}
                >
                  <Typography>Download File</Typography>
                </Paper>
              </a>
            </Box>
          </Box>
        );
    }
  };
  
  return (
    <Paper 
      elevation={3}
      sx={{ 
        width, 
        height, 
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Optional file name/info header */}
      {fileName && (
        <Box sx={{ 
          px: 2, 
          py: 1, 
          borderBottom: 1, 
          borderColor: 'divider',
          bgcolor: 'background.default',
        }}>
          <Typography variant="subtitle1" noWrap>
            {fileName}
          </Typography>
        </Box>
      )}
      
      {/* File content area */}
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {renderFileContent()}
      </Box>
    </Paper>
  );
};

export default FileViewer;
