#!/usr/bin/env python3
"""
Fix Content Preview in Generator Pages

This script fixes the content preview issues in the generator pages
of the GenAI Agent 3D project by updating frontend components and paths.
"""

import os
import sys
import re
import json
from pathlib import Path
import logging
import shutil
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_frontend_files(project_root):
    """Find relevant frontend files for content preview"""
    logger.info("Searching for frontend files...")
    
    # Path to frontend directory
    frontend_dir = project_root / "genai_agent_project" / "web" / "frontend"
    
    if not frontend_dir.exists():
        logger.error(f"Frontend directory not found: {frontend_dir}")
        return {}
    
    # Look for relevant files
    component_files = {}
    
    # Common component files that handle content preview
    common_components = [
        "src/components/ModelPreview.jsx",
        "src/components/ScenePreview.jsx",
        "src/components/DiagramPreview.jsx",
        "src/components/ContentPreview.jsx",
        "src/components/PreviewPanel.jsx",
        "src/pages/ModelGenerator.jsx",
        "src/pages/SceneGenerator.jsx",
        "src/pages/DiagramGenerator.jsx"
    ]
    
    # Find files based on common names
    for component_path in common_components:
        full_path = frontend_dir / component_path
        if full_path.exists():
            component_files[component_path] = full_path
            logger.info(f"Found component file: {full_path}")
    
    # Search for additional files containing "preview" or "generator"
    src_dir = frontend_dir / "src"
    if src_dir.exists():
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith((".jsx", ".js", ".tsx", ".ts")) and ("preview" in file.lower() or "generator" in file.lower()):
                    rel_path = os.path.relpath(os.path.join(root, file), frontend_dir)
                    full_path = Path(os.path.join(root, file))
                    if rel_path not in component_files:
                        component_files[rel_path] = full_path
                        logger.info(f"Found additional component file: {full_path}")
    
    return component_files

def fix_path_handling(file_path):
    """Fix path handling in a frontend component file"""
    logger.info(f"Fixing path handling in: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Original content for backup
        original_content = content
        
        # Fix common path issues
        
        # 1. Fix hardcoded paths
        content = re.sub(
            r'(["\'`])\/(?:public\/|genai_agent_project\/output\/|output\/)(models|scenes|diagrams|svg)\/(.*?)(["\'`])',
            r'\1/\2/\3\4',
            content
        )
        
        # 2. Fix incorrect path concatenation
        content = re.sub(
            r'(process\.env\.PUBLIC_URL\s*\+\s*["\'])\/?(models|scenes|diagrams|svg)\/(.*?)(["\'])',
            r'\1/\2/\3\4',
            content
        )
        
        # 3. Add path validation and fallbacks
        if "src=" in content and ("models/" in content or "scenes/" in content or "diagrams/" in content or "svg/" in content):
            # For image elements with src attributes
            content = re.sub(
                r'src={`(.*?)(models|scenes|diagrams|svg)\/(.*?)`}',
                r'src={`\1\2/\3`} onError={(e) => { e.target.onerror = null; e.target.src = "/placeholder.png"; }}',
                content
            )
        
        # 4. Add loading state handling
        if "useState" in content and not "isLoading" in content:
            # Add loading state
            content = re.sub(
                r'(const\s+\[\s*.*?\s*,\s*set.*?\s*\]\s*=\s*useState\([^)]*\);)',
                r'\1\n  const [isLoading, setIsLoading] = useState(false);',
                content
            )
            
            # Add loading indicator
            if "<div className=" in content and not "Loading..." in content:
                content = re.sub(
                    r'(<div className=["\'].*?["\']>)',
                    r'\1\n        {isLoading && <div className="loading-indicator">Loading...</div>}',
                    content
                )
        
        # 5. Add retry functionality for file loading
        if "fetch(" in content and not "retryCount" in content:
            content = re.sub(
                r'(const\s+fetchData\s*=\s*(?:async\s*)?\(\)\s*=>\s*{)',
                r'\1\n    let retryCount = 0;\n    const maxRetries = 3;',
                content
            )
            
            content = re.sub(
                r'(catch\s*\(\s*error\s*\)\s*{)',
                r'\1\n      if (retryCount < maxRetries) {\n        retryCount++;\n        console.log(`Retrying fetch (${retryCount}/${maxRetries})...`);\n        setTimeout(fetchData, 1000);\n        return;\n      }',
                content
            )
        
        # If content has changed, write it back
        if content != original_content:
            # Create a backup
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated file: {file_path}")
            return True
        else:
            logger.info(f"No changes needed in: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error fixing {file_path}: {str(e)}")
        return False

def add_placeholder_image(project_root):
    """Add placeholder image for missing content"""
    logger.info("Adding placeholder image...")
    
    # Path to public directory
    public_dir = project_root / "genai_agent_project" / "web" / "frontend" / "public"
    placeholder_path = public_dir / "placeholder.png"
    
    if placeholder_path.exists():
        logger.info(f"Placeholder image already exists: {placeholder_path}")
        return True
    
    try:
        # Create a simple placeholder image (1x1 pixel transparent PNG)
        # This is a minimal valid PNG file
        placeholder_data = bytes.fromhex(
            '89504e470d0a1a0a0000000d4948445200000080000000800806000000c33e61cb'
            '0000000970485973000016250000162501495224f00000001c69444f5448c7ed9a'
            '010a00300c03fffe3f7ae2307416d5c25048d9b1e59500ccc2e4aaaa9ec077810'
            '4113681200134024c01e81e6cc751afff0e6fd3c000980004c01e841f0ed8f3c0'
            '00980004c00e803740012202d32da4bd0000000049454e44ae426082'
        )
        
        # Ensure the public directory exists
        public_dir.mkdir(exist_ok=True, parents=True)
        
        # Write the placeholder image
        with open(placeholder_path, 'wb') as f:
            f.write(placeholder_data)
        
        logger.info(f"Created placeholder image: {placeholder_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating placeholder image: {str(e)}")
        return False

def add_loading_indicator_css(project_root):
    """Add CSS for loading indicator"""
    logger.info("Adding loading indicator CSS...")
    
    # Path to CSS file
    css_path = project_root / "genai_agent_project" / "web" / "frontend" / "src" / "App.css"
    
    if not css_path.exists():
        logger.warning(f"CSS file not found: {css_path}")
        return False
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if loading indicator styles already exist
        if ".loading-indicator" in content:
            logger.info("Loading indicator styles already exist")
            return True
        
        # Add loading indicator styles
        loading_styles = """
/* Loading indicator styles */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-weight: bold;
  color: #666;
}

.loading-indicator::after {
  content: " ";
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-left: 12px;
  border: 3px solid #ccc;
  border-radius: 50%;
  border-top-color: #666;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #fff5f5;
  border: 1px solid #ffebeb;
  border-radius: 4px;
  color: #d63031;
  text-align: center;
  margin: 10px 0;
}

.preview-error p {
  margin: 0;
  padding: 5px 0;
}

.preview-error button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #0984e3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.preview-error button:hover {
  background-color: #0876cc;
}
"""
        
        # Add the styles to the end of the file
        with open(css_path, 'a', encoding='utf-8') as f:
            f.write(loading_styles)
        
        logger.info(f"Added loading indicator styles to: {css_path}")
        return True
    except Exception as e:
        logger.error(f"Error adding loading indicator styles: {str(e)}")
        return False

def create_refresh_hook(project_root):
    """Create a hook for refreshing content"""
    logger.info("Creating refresh hook...")
    
    # Path to hooks directory
    hooks_dir = project_root / "genai_agent_project" / "web" / "frontend" / "src" / "hooks"
    refresh_hook_path = hooks_dir / "useContentRefresh.js"
    
    # Check if the hook already exists
    if refresh_hook_path.exists():
        logger.info(f"Refresh hook already exists: {refresh_hook_path}")
        return True
    
    # Ensure hooks directory exists
    hooks_dir.mkdir(exist_ok=True, parents=True)
    
    try:
        # Create the hook file
        refresh_hook_content = """import { useState, useEffect, useCallback } from 'react';

/**
 * Hook for refreshing content with retry and error handling
 * 
 * @param {Function} fetchFunction - Function to fetch the content
 * @param {number} interval - Refresh interval in milliseconds (default: 2000)
 * @param {number} maxRetries - Maximum number of retries on error (default: 3)
 * @param {boolean} autoRefresh - Whether to automatically refresh (default: true)
 * @returns {Object} - { data, loading, error, refresh, retryCount }
 */
const useContentRefresh = (
  fetchFunction,
  interval = 2000,
  maxRetries = 3,
  autoRefresh = true
) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [timerId, setTimerId] = useState(null);

  // Function to fetch data with retry logic
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchFunction();
      setData(result);
      setError(null);
      setRetryCount(0);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching content:', err);
      if (retryCount < maxRetries) {
        setRetryCount(prev => prev + 1);
        // Retry with exponential backoff
        const backoff = Math.min(1000 * Math.pow(2, retryCount), 10000);
        console.log(`Retrying in ${backoff}ms (${retryCount + 1}/${maxRetries})`);
        setTimeout(fetchData, backoff);
      } else {
        setError(err.message || 'Failed to load content');
        setLoading(false);
      }
    }
  }, [fetchFunction, retryCount, maxRetries]);

  // Function to manually refresh
  const refresh = useCallback(() => {
    setRetryCount(0);
    fetchData();
  }, [fetchData]);

  // Set up auto-refresh
  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set up interval for auto-refresh if enabled
    if (autoRefresh && interval > 0) {
      const id = setInterval(refresh, interval);
      setTimerId(id);
      return () => clearInterval(id);
    }
    return undefined;
  }, [fetchData, refresh, autoRefresh, interval]);

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (timerId) {
        clearInterval(timerId);
      }
    };
  }, [timerId]);

  return { data, loading, error, refresh, retryCount };
};

export default useContentRefresh;
"""
        
        # Write the hook file
        with open(refresh_hook_path, 'w', encoding='utf-8') as f:
            f.write(refresh_hook_content)
        
        logger.info(f"Created refresh hook: {refresh_hook_path}")
        
        # Create an index.js file to export the hook
        index_path = hooks_dir / "index.js"
        if not index_path.exists():
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("export { default as useContentRefresh } from './useContentRefresh';\n")
            logger.info(f"Created hooks index: {index_path}")
        else:
            # Check if the hook is already exported
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "useContentRefresh" not in content:
                with open(index_path, 'a', encoding='utf-8') as f:
                    f.write("export { default as useContentRefresh } from './useContentRefresh';\n")
                logger.info(f"Updated hooks index: {index_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating refresh hook: {str(e)}")
        return False

def create_preview_component(project_root):
    """Create a reusable preview component"""
    logger.info("Creating enhanced preview component...")
    
    # Path to components directory
    components_dir = project_root / "genai_agent_project" / "web" / "frontend" / "src" / "components"
    preview_component_path = components_dir / "EnhancedPreview.jsx"
    
    # Check if the component already exists
    if preview_component_path.exists():
        logger.info(f"Enhanced preview component already exists: {preview_component_path}")
        return True
    
    # Ensure components directory exists
    components_dir.mkdir(exist_ok=True, parents=True)
    
    try:
        # Create the component file
        preview_component_content = """import React, { useState, useEffect } from 'react';
import { useContentRefresh } from '../hooks';

/**
 * Enhanced content preview component with auto-refresh, error handling, and retry logic
 * 
 * @param {Object} props - Component props
 * @param {string} props.src - The source URL for the content
 * @param {string} props.type - The type of content ('image', 'svg', 'model', 'scene')
 * @param {string} props.alt - Alternative text for the content
 * @param {Object} props.style - Custom styles for the container
 * @param {number} props.refreshInterval - Interval for auto-refresh in ms (default: 2000)
 * @param {boolean} props.autoRefresh - Whether to automatically refresh (default: true)
 * @returns {JSX.Element} - The rendered component
 */
const EnhancedPreview = ({
  src,
  type = 'image',
  alt = 'Preview content',
  style = {},
  refreshInterval = 2000,
  autoRefresh = true,
  className = '',
  onLoad = () => {},
  onError = () => {},
}) => {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [loadFailed, setLoadFailed] = useState(false);
  
  // Function to fetch the content
  const fetchContent = async () => {
    try {
      // For images, we just need to check if they exist
      const response = await fetch(src, { method: 'HEAD' });
      
      if (!response.ok) {
        throw new Error(`Failed to load content: ${response.status} ${response.statusText}`);
      }
      
      // Reset load failed state if previously failed
      setLoadFailed(false);
      return src;
    } catch (error) {
      console.error(`Error loading ${type} from ${src}:`, error);
      setLoadFailed(true);
      throw error;
    }
  };
  
  // Use the content refresh hook
  const { loading, error, refresh } = useContentRefresh(
    fetchContent,
    refreshInterval,
    3,
    autoRefresh
  );
  
  // Update dimensions on window resize
  useEffect(() => {
    const updateDimensions = () => {
      const container = document.getElementById('preview-container');
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: container.clientHeight,
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);
  
  // Handle image error
  const handleImageError = (e) => {
    e.target.onerror = null;
    e.target.src = '/placeholder.png';
    setLoadFailed(true);
    onError(e);
  };
  
  // Render content based on type
  const renderContent = () => {
    if (loading) {
      return (
        <div className="loading-indicator">
          Loading preview...
        </div>
      );
    }
    
    if (error || loadFailed) {
      return (
        <div className="preview-error">
          <p>Unable to load preview</p>
          <p>The file may not exist or is still being generated</p>
          <button onClick={refresh}>
            Retry
          </button>
        </div>
      );
    }
    
    switch (type.toLowerCase()) {
      case 'image':
        return (
          <img 
            src={src} 
            alt={alt} 
            onError={handleImageError}
            onLoad={onLoad}
            style={{ maxWidth: '100%', maxHeight: '100%' }}
          />
        );
      
      case 'svg':
        return (
          <object 
            data={src} 
            type="image/svg+xml"
            onError={() => setLoadFailed(true)}
            onLoad={onLoad}
            style={{ width: '100%', height: '100%' }}
          >
            <img src="/placeholder.png" alt="SVG fallback" />
          </object>
        );
      
      case 'model':
        // This assumes you have a 3D model viewer component
        // You'd need to implement or import a proper 3D viewer
        return (
          <div className="model-placeholder">
            <img src={src} alt={alt} onError={handleImageError} onLoad={onLoad} />
            <p>3D Model Preview (thumbnail)</p>
          </div>
        );
      
      case 'scene':
        // This assumes you have a scene viewer component
        return (
          <div className="scene-placeholder">
            <img src={src} alt={alt} onError={handleImageError} onLoad={onLoad} />
            <p>Scene Preview (thumbnail)</p>
          </div>
        );
      
      default:
        return (
          <div className="unknown-content-type">
            <p>Unknown content type: {type}</p>
            <a href={src} target="_blank" rel="noopener noreferrer">View Raw Content</a>
          </div>
        );
    }
  };
  
  return (
    <div 
      id="preview-container"
      className={`enhanced-preview-container ${className}`}
      style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '200px',
        border: '1px solid #eee',
        borderRadius: '4px',
        padding: '10px',
        ...style 
      }}
    >
      {renderContent()}
    </div>
  );
};

export default EnhancedPreview;
"""
        
        # Write the component file
        with open(preview_component_path, 'w', encoding='utf-8') as f:
            f.write(preview_component_content)
        
        logger.info(f"Created enhanced preview component: {preview_component_path}")
        
        # Update the components index if it exists
        index_path = components_dir / "index.js"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "EnhancedPreview" not in content:
                with open(index_path, 'a', encoding='utf-8') as f:
                    f.write("export { default as EnhancedPreview } from './EnhancedPreview';\n")
                logger.info(f"Updated components index: {index_path}")
        else:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("export { default as EnhancedPreview } from './EnhancedPreview';\n")
            logger.info(f"Created components index: {index_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating enhanced preview component: {str(e)}")
        return False

def main():
    """Main function"""
    # Get project root
    project_root = Path(__file__).parent.absolute()
    
    print("===========================================")
    print("  Fix Content Preview - GenAI Agent 3D")
    print("===========================================")
    print(f"Project root: {project_root}")
    
    # Find frontend files
    component_files = find_frontend_files(project_root)
    
    if not component_files:
        print("No frontend files found. Make sure the project structure is correct.")
        return 1
    
    # Add placeholder image
    add_placeholder_image(project_root)
    
    # Add loading indicator CSS
    add_loading_indicator_css(project_root)
    
    # Create refresh hook
    create_refresh_hook(project_root)
    
    # Create enhanced preview component
    create_preview_component(project_root)
    
    # Fix path handling in component files
    updated_files = 0
    for rel_path, file_path in component_files.items():
        if fix_path_handling(file_path):
            updated_files += 1
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Frontend files found: {len(component_files)}")
    print(f"Files updated: {updated_files}")
    
    print("\n✅ Content preview fixes have been applied.")
    print("To see the changes, rebuild the frontend application.")
    
    # Provide rebuild instructions
    print("\nTo rebuild the frontend:")
    print("1. Navigate to the frontend directory:")
    print("   cd genai_agent_project/web/frontend")
    print("2. Install dependencies if needed:")
    print("   npm install")
    print("3. Build the application:")
    print("   npm run build")
    print("4. Restart the services:")
    print("   python restart_services.py")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
