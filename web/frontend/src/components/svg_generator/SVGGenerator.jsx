import React, { useState, useEffect } from 'react';
import './SVGGenerator.css';

/**
 * SVG Generator Component
 * 
 * This component provides a user interface for generating SVG diagrams from text descriptions
 * using various LLM providers, and allows converting the SVGs to 3D models and videos.
 */
const SVGGenerator = () => {
  // State variables
  const [concept, setConcept] = useState('');
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [svgContent, setSvgContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  // Fetch available providers on component mount
  useEffect(() => {
    fetchProviders();
  }, []);

  // Poll task status if a task is in progress
  useEffect(() => {
    let interval;
    if (taskId) {
      interval = setInterval(() => {
        checkTaskStatus(taskId);
      }, 2000); // Check every 2 seconds
    }
    return () => clearInterval(interval);
  }, [taskId]);

  // Fetch available LLM providers
  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/svg-to-video/providers');
      if (response.ok) {
        const data = await response.json();
        setProviders(data);
        if (data.length > 0) {
          setSelectedProvider(data[0]);
        }
      } else {
        console.error('Failed to fetch providers');
        setErrorMessage('Failed to fetch providers');
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
      setErrorMessage(`Error fetching providers: ${error.message}`);
    }
  };

  // Generate SVG
  const generateSVG = async () => {
    if (!concept.trim()) {
      setErrorMessage('Please enter a concept description');
      return;
    }

    setIsGenerating(true);
    setErrorMessage('');
    setSvgContent('');

    try {
      const response = await fetch('/api/svg-to-video/generate-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          concept,
          provider: selectedProvider,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSvgContent(data.svg_content);
      } else {
        const errorData = await response.json();
        setErrorMessage(`Failed to generate SVG: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error generating SVG:', error);
      setErrorMessage(`Error generating SVG: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // Convert SVG to Video
  const convertToVideo = async () => {
    if (!svgContent) {
      setErrorMessage('Please generate an SVG first');
      return;
    }

    setIsConverting(true);
    setErrorMessage('');
    setTaskId(null);
    setTaskStatus(null);

    try {
      // Create a blob from the SVG content
      const svgBlob = new Blob([svgContent], { type: 'image/svg+xml' });
      
      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append('svg_file', svgBlob, 'diagram.svg');
      formData.append('render_quality', 'medium');
      formData.append('animation_type', 'standard');
      
      const response = await fetch('/api/svg-to-video/convert-svg', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setTaskId(data.task_id);
      } else {
        const errorData = await response.json();
        setErrorMessage(`Failed to start conversion: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error starting conversion:', error);
      setErrorMessage(`Error starting conversion: ${error.message}`);
    } finally {
      setIsConverting(false);
    }
  };

  // Check task status
  const checkTaskStatus = async (id) => {
    try {
      const response = await fetch(`/api/svg-to-video/task/${id}`);
      if (response.ok) {
        const data = await response.json();
        setTaskStatus(data);
        
        // If task is completed or failed, stop polling
        if (data.status === 'completed' || data.status === 'failed') {
          setTaskId(null);
        }
      } else {
        console.error('Failed to check task status');
        setTaskId(null);
      }
    } catch (error) {
      console.error('Error checking task status:', error);
      setTaskId(null);
    }
  };

  // Generate and convert in one step
  const generateAndConvert = async () => {
    if (!concept.trim()) {
      setErrorMessage('Please enter a concept description');
      return;
    }

    setIsGenerating(true);
    setErrorMessage('');
    setTaskId(null);
    setTaskStatus(null);

    try {
      const response = await fetch('/api/svg-to-video/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          concept,
          provider: selectedProvider,
          render_quality: 'medium',
          animation_type: 'standard',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setTaskId(data.task_id);
      } else {
        const errorData = await response.json();
        setErrorMessage(`Failed to start generation: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error starting generation:', error);
      setErrorMessage(`Error starting generation: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="svg-generator">
      <h2>SVG Generator</h2>
      
      <div className="input-section">
        <div className="form-group">
          <label htmlFor="concept">Concept Description:</label>
          <textarea
            id="concept"
            value={concept}
            onChange={(e) => setConcept(e.target.value)}
            placeholder="Describe the diagram you want to generate (e.g., 'A flowchart showing user registration process')"
            rows={5}
            disabled={isGenerating || isConverting}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="provider">LLM Provider:</label>
          <select
            id="provider"
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            disabled={isGenerating || isConverting || providers.length === 0}
          >
            {providers.map((provider) => (
              <option key={provider} value={provider}>{provider}</option>
            ))}
          </select>
        </div>
        
        <div className="button-group">
          <button 
            onClick={generateSVG} 
            disabled={isGenerating || isConverting || !concept.trim()}
          >
            {isGenerating ? 'Generating...' : 'Generate SVG'}
          </button>
          <button 
            onClick={convertToVideo} 
            disabled={isGenerating || isConverting || !svgContent}
          >
            {isConverting ? 'Converting...' : 'Convert to Video'}
          </button>
          <button 
            onClick={generateAndConvert} 
            disabled={isGenerating || isConverting || !concept.trim()}
          >
            Generate & Convert
          </button>
        </div>
        
        {errorMessage && (
          <div className="error-message">
            {errorMessage}
          </div>
        )}
      </div>
      
      <div className="output-section">
        {svgContent && (
          <div className="svg-preview">
            <h3>SVG Preview</h3>
            <div 
              dangerouslySetInnerHTML={{ __html: svgContent }} 
              className="svg-container"
            />
            <button 
              onClick={() => {
                const blob = new Blob([svgContent], { type: 'image/svg+xml' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'diagram.svg';
                document.body.appendChild(a);
                a.click();
                URL.revokeObjectURL(url);
                document.body.removeChild(a);
              }}
              className="download-button"
            >
              Download SVG
            </button>
          </div>
        )}
        
        {taskStatus && (
          <div className="task-status">
            <h3>Conversion Status</h3>
            <div className="status-info">
              <p>Status: <span className={`status-${taskStatus.status}`}>{taskStatus.status}</span></p>
              {taskStatus.progress !== undefined && (
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${taskStatus.progress}%` }}
                  />
                </div>
              )}
              
              {taskStatus.status === 'completed' && taskStatus.result && (
                <div className="result-info">
                  <p>Video generated successfully!</p>
                  <a 
                    href={`/outputs/${taskStatus.result.output_path.split('/').pop()}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="download-link"
                  >
                    Download Video
                  </a>
                </div>
              )}
              
              {taskStatus.status === 'failed' && (
                <div className="error-info">
                  <p>Error: {taskStatus.error}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SVGGenerator;
