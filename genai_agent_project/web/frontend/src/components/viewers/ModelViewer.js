import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader';
import { Box, Typography, LinearProgress, CircularProgress, Paper } from '@mui/material';

const ModelViewer = ({ modelUrl, modelType = 'gltf', width = '100%', height = '400px' }) => {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(0);
  
  useEffect(() => {
    if (!containerRef.current || !modelUrl) return;
    
    let renderer, scene, camera, controls, model;
    
    // Initialize renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    
    // Initialize scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    
    // Initialize camera
    camera = new THREE.PerspectiveCamera(
      45,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(5, 5, 5);
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    
    const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x080820, 0.5);
    scene.add(hemisphereLight);
    
    // Add grid helper
    const gridHelper = new THREE.GridHelper(10, 10);
    scene.add(gridHelper);
    
    // Add axes helper
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);
    
    // Initialize orbit controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    
    // Determine which loader to use based on model type
    let loader;
    switch (modelType.toLowerCase()) {
      case 'gltf':
      case 'glb':
        loader = new GLTFLoader();
        break;
      case 'obj':
        loader = new OBJLoader();
        break;
      case 'stl':
        loader = new STLLoader();
        break;
      case 'ply':
        loader = new PLYLoader();
        break;
      default:
        setError(`Unsupported model type: ${modelType}`);
        setLoading(false);
        return;
    }
    
    // Set up loading manager
    const loadingManager = new THREE.LoadingManager();
    loadingManager.onProgress = (url, itemsLoaded, itemsTotal) => {
      setLoadingProgress((itemsLoaded / itemsTotal) * 100);
    };
    
    loadingManager.onError = (url) => {
      setError(`Error loading: ${url}`);
      setLoading(false);
    };
    
    loader.manager = loadingManager;
    
    // Load the model
    const loadModel = () => {
      // Reset in case we're loading a new model
      setLoading(true);
      setError(null);
      
      // Clear any existing model
      if (model) {
        scene.remove(model);
        // Dispose geometry and materials to prevent memory leaks
        if (model.traverse) {
          model.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
              if (Array.isArray(child.material)) {
                child.material.forEach(material => material.dispose());
              } else {
                child.material.dispose();
              }
            }
          });
        }
      }
      
      // Handle different loaders
      if (modelType.toLowerCase() === 'gltf' || modelType.toLowerCase() === 'glb') {
        loader.load(
          modelUrl,
          (gltf) => {
            model = gltf.scene;
            
            // Center the model
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            // Normalize model size
            const maxSize = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxSize;
            model.scale.set(scale, scale, scale);
            
            // Move model to center
            model.position.sub(center.multiplyScalar(scale));
            
            // Enable shadows
            model.traverse((node) => {
              if (node.isMesh) {
                node.castShadow = true;
                node.receiveShadow = true;
              }
            });
            
            scene.add(model);
            setLoading(false);
            
            // Update camera to focus on model
            controls.target.set(0, 0, 0);
            controls.update();
          },
          (xhr) => {
            setLoadingProgress((xhr.loaded / xhr.total) * 100);
          },
          (error) => {
            console.error('Error loading GLTF model:', error);
            setError('Failed to load model');
            setLoading(false);
          }
        );
      } else if (modelType.toLowerCase() === 'obj') {
        loader.load(
          modelUrl,
          (obj) => {
            model = obj;
            
            // Center the model
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            // Normalize model size
            const maxSize = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxSize;
            model.scale.set(scale, scale, scale);
            
            // Move model to center
            model.position.sub(center.multiplyScalar(scale));
            
            // Enable shadows
            model.traverse((node) => {
              if (node.isMesh) {
                node.castShadow = true;
                node.receiveShadow = true;
              }
            });
            
            scene.add(model);
            setLoading(false);
            
            // Update camera to focus on model
            controls.target.set(0, 0, 0);
            controls.update();
          },
          (xhr) => {
            setLoadingProgress((xhr.loaded / xhr.total) * 100);
          },
          (error) => {
            console.error('Error loading OBJ model:', error);
            setError('Failed to load model');
            setLoading(false);
          }
        );
      } else if (modelType.toLowerCase() === 'stl') {
        loader.load(
          modelUrl,
          (geometry) => {
            const material = new THREE.MeshStandardMaterial({
              color: 0x8888ff,
              metalness: 0.3,
              roughness: 0.6,
            });
            
            const mesh = new THREE.Mesh(geometry, material);
            model = mesh;
            
            // Center the model
            geometry.computeBoundingBox();
            const box = geometry.boundingBox;
            const center = new THREE.Vector3();
            box.getCenter(center);
            
            geometry.translate(-center.x, -center.y, -center.z);
            
            // Normalize model size
            const size = new THREE.Vector3();
            box.getSize(size);
            const maxSize = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxSize;
            model.scale.set(scale, scale, scale);
            
            // Enable shadows
            model.castShadow = true;
            model.receiveShadow = true;
            
            scene.add(model);
            setLoading(false);
            
            // Update camera to focus on model
            controls.target.set(0, 0, 0);
            controls.update();
          },
          (xhr) => {
            setLoadingProgress((xhr.loaded / xhr.total) * 100);
          },
          (error) => {
            console.error('Error loading STL model:', error);
            setError('Failed to load model');
            setLoading(false);
          }
        );
      } else if (modelType.toLowerCase() === 'ply') {
        loader.load(
          modelUrl,
          (geometry) => {
            const material = new THREE.MeshStandardMaterial({
              color: 0x8888ff,
              metalness: 0.3,
              roughness: 0.6,
              vertexColors: geometry.hasAttribute('color')
            });
            
            const mesh = new THREE.Mesh(geometry, material);
            model = mesh;
            
            // Center the model
            geometry.computeBoundingBox();
            const box = geometry.boundingBox;
            const center = new THREE.Vector3();
            box.getCenter(center);
            
            geometry.translate(-center.x, -center.y, -center.z);
            
            // Normalize model size
            const size = new THREE.Vector3();
            box.getSize(size);
            const maxSize = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxSize;
            model.scale.set(scale, scale, scale);
            
            // Enable shadows
            model.castShadow = true;
            model.receiveShadow = true;
            
            scene.add(model);
            setLoading(false);
            
            // Update camera to focus on model
            controls.target.set(0, 0, 0);
            controls.update();
          },
          (xhr) => {
            setLoadingProgress((xhr.loaded / xhr.total) * 100);
          },
          (error) => {
            console.error('Error loading PLY model:', error);
            setError('Failed to load model');
            setLoading(false);
          }
        );
      }
    };
    
    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    
    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Start animation
    animate();
    
    // Load model if URL is provided
    if (modelUrl) {
      loadModel();
    } else {
      setLoading(false);
    }
    
    // Clean up on unmount
    return () => {
      window.removeEventListener('resize', handleResize);
      
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      
      // Dispose resources
      if (renderer) {
        renderer.dispose();
      }
      
      if (controls) {
        controls.dispose();
      }
      
      if (model) {
        scene.remove(model);
        // Dispose geometry and materials
        if (model.traverse) {
          model.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
              if (Array.isArray(child.material)) {
                child.material.forEach(material => material.dispose());
              } else {
                child.material.dispose();
              }
            }
          });
        }
      }
    };
  }, [modelUrl, modelType]);
  
  return (
    <Box sx={{ position: 'relative', width, height, overflow: 'hidden' }}>
      <Paper
        ref={containerRef}
        elevation={3}
        sx={{
          width: '100%',
          height: '100%',
          bgcolor: 'background.default',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {/* Loading overlay */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              zIndex: 10,
            }}
          >
            <CircularProgress size={50} />
            <Typography variant="body1" sx={{ mt: 2 }}>Loading Model...</Typography>
            <Box sx={{ width: '60%', mt: 1 }}>
              <LinearProgress variant="determinate" value={loadingProgress} />
              <Typography variant="caption" textAlign="center" display="block">
                {Math.round(loadingProgress)}%
              </Typography>
            </Box>
          </Box>
        )}
        
        {/* Error message */}
        {error && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              zIndex: 10,
            }}
          >
            <Typography variant="h6" color="error">Error</Typography>
            <Typography variant="body1" color="error">
              {error}
            </Typography>
          </Box>
        )}
        
        {/* No model message */}
        {!loading && !error && !modelUrl && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              zIndex: 10,
            }}
          >
            <Typography variant="h6">No Model Selected</Typography>
            <Typography variant="body1">
              Please select a model to view
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default ModelViewer;
