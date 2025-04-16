"""
Asset Manager Service for managing 3D assets
"""

import logging
import os
import shutil
import json
import uuid
import zipfile
import hashlib
from typing import Dict, Any, List, Optional, BinaryIO, Union

from genai_agent.services.redis_bus import RedisMessageBus

logger = logging.getLogger(__name__)

class AssetManager:
    """
    Service for managing 3D assets
    
    Handles storage, retrieval, and metadata for 3D assets like models,
    textures, materials, and other resources.
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any] = None):
        """
        Initialize Asset Manager
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Configuration parameters
        """
        self.redis_bus = redis_bus
        self.config = config or {}
        
        # Asset storage path
        self.storage_path = self.config.get('storage_path', 'data/assets/')
        
        # Redis key prefix for asset metadata
        self.key_prefix = 'asset:'
        
        # Asset categories
        self.categories = {
            'model': ['obj', 'fbx', 'glb', 'gltf', 'blend', 'dae'],
            'texture': ['png', 'jpg', 'jpeg', 'tga', 'bmp', 'tif', 'tiff', 'exr', 'hdr'],
            'material': ['mtl', 'mat'],
            'script': ['py', 'js'],
            'other': []
        }
        
        logger.info("Asset Manager initialized")
        
        # Create storage directory if needed
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            
        # Create category directories
        for category in self.categories:
            category_path = os.path.join(self.storage_path, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
    
    async def store_asset(self, file_path: str, metadata: Optional[Dict[str, Any]] = None,
                        category: Optional[str] = None) -> Optional[str]:
        """
        Store an asset
        
        Args:
            file_path: Path to asset file
            metadata: Asset metadata
            category: Asset category (auto-detected if None)
            
        Returns:
            Asset ID or None if failed
        """
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Asset file not found: {file_path}")
            return None
        
        try:
            # Generate asset ID
            asset_id = str(uuid.uuid4())
            
            # Determine category from extension if not provided
            if category is None:
                ext = os.path.splitext(file_path)[1].lower()[1:]  # Remove dot
                category = self._get_category(ext)
            
            # Create metadata
            if metadata is None:
                metadata = {}
            
            # Add basic metadata
            metadata.update({
                'id': asset_id,
                'filename': os.path.basename(file_path),
                'extension': os.path.splitext(file_path)[1].lower()[1:],
                'category': category,
                'file_size': os.path.getsize(file_path),
                'md5_hash': self._calculate_file_hash(file_path)
            })
            
            # Store asset file
            dest_path = os.path.join(self.storage_path, category, f"{asset_id}{os.path.splitext(file_path)[1]}")
            shutil.copy2(file_path, dest_path)
            
            # Store metadata
            await self._store_metadata(asset_id, metadata)
            
            logger.info(f"Stored asset: {metadata['filename']} ({asset_id})")
            return asset_id
        except Exception as e:
            logger.error(f"Error storing asset: {str(e)}")
            return None
    
    async def store_asset_from_memory(self, file_data: bytes, filename: str, 
                                    metadata: Optional[Dict[str, Any]] = None,
                                    category: Optional[str] = None) -> Optional[str]:
        """
        Store an asset from memory
        
        Args:
            file_data: Asset file data
            filename: Asset filename
            metadata: Asset metadata
            category: Asset category (auto-detected if None)
            
        Returns:
            Asset ID or None if failed
        """
        try:
            # Generate asset ID
            asset_id = str(uuid.uuid4())
            
            # Determine category from extension if not provided
            if category is None:
                ext = os.path.splitext(filename)[1].lower()[1:]  # Remove dot
                category = self._get_category(ext)
            
            # Create metadata
            if metadata is None:
                metadata = {}
            
            # Add basic metadata
            metadata.update({
                'id': asset_id,
                'filename': filename,
                'extension': os.path.splitext(filename)[1].lower()[1:],
                'category': category,
                'file_size': len(file_data),
                'md5_hash': hashlib.md5(file_data).hexdigest()
            })
            
            # Store asset file
            dest_path = os.path.join(self.storage_path, category, f"{asset_id}{os.path.splitext(filename)[1]}")
            with open(dest_path, 'wb') as f:
                f.write(file_data)
            
            # Store metadata
            await self._store_metadata(asset_id, metadata)
            
            logger.info(f"Stored asset from memory: {filename} ({asset_id})")
            return asset_id
        except Exception as e:
            logger.error(f"Error storing asset from memory: {str(e)}")
            return None
    
    async def get_asset_path(self, asset_id: str) -> Optional[str]:
        """
        Get the path to an asset file
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Path to asset file or None if not found
        """
        metadata = await self.get_asset_metadata(asset_id)
        if not metadata:
            return None
        
        category = metadata.get('category', 'other')
        extension = metadata.get('extension', '')
        path = os.path.join(self.storage_path, category, f"{asset_id}.{extension}")
        
        if not os.path.exists(path):
            return None
        
        return path
    
    async def get_asset_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get asset metadata
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Asset metadata or None if not found
        """
        if not await self.redis_bus.connect():
            logger.error("Cannot get asset metadata: Redis connection failed")
            return None
        
        key = f"{self.key_prefix}{asset_id}"
        
        try:
            # Get from Redis
            metadata_str = await self.redis_bus.redis.get(key)
            
            if metadata_str is None:
                return None
            
            # Parse metadata
            if isinstance(metadata_str, bytes):
                metadata_str = metadata_str.decode('utf-8')
            
            return json.loads(metadata_str)
        except Exception as e:
            logger.error(f"Error getting asset metadata: {str(e)}")
            return None
    
    async def update_asset_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update asset metadata
        
        Args:
            asset_id: Asset ID
            metadata: New metadata (will be merged with existing)
            
        Returns:
            True if updated successfully, False otherwise
        """
        # Get existing metadata
        existing = await self.get_asset_metadata(asset_id)
        if not existing:
            return False
        
        # Merge metadata
        existing.update(metadata)
        
        # Store updated metadata
        return await self._store_metadata(asset_id, existing)
    
    async def delete_asset(self, asset_id: str) -> bool:
        """
        Delete an asset
        
        Args:
            asset_id: Asset ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        # Get asset metadata for file path
        metadata = await self.get_asset_metadata(asset_id)
        if not metadata:
            return False
        
        try:
            # Delete asset file
            category = metadata.get('category', 'other')
            extension = metadata.get('extension', '')
            file_path = os.path.join(self.storage_path, category, f"{asset_id}.{extension}")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete metadata
            if not await self.redis_bus.connect():
                logger.error("Cannot delete asset metadata: Redis connection failed")
                return False
            
            key = f"{self.key_prefix}{asset_id}"
            await self.redis_bus.redis.delete(key)
            
            logger.info(f"Deleted asset: {metadata.get('filename')} ({asset_id})")
            return True
        except Exception as e:
            logger.error(f"Error deleting asset: {str(e)}")
            return False
    
    async def list_assets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List assets
        
        Args:
            category: Filter by category
            
        Returns:
            List of asset metadata
        """
        if not await self.redis_bus.connect():
            logger.error("Cannot list assets: Redis connection failed")
            return []
        
        try:
            # Get all asset keys
            keys = await self.redis_bus.redis.keys(f"{self.key_prefix}*")
            
            assets = []
            for key in keys:
                # Get metadata
                metadata_str = await self.redis_bus.redis.get(key)
                
                if metadata_str is None:
                    continue
                
                # Parse metadata
                if isinstance(metadata_str, bytes):
                    metadata_str = metadata_str.decode('utf-8')
                
                metadata = json.loads(metadata_str)
                
                # Filter by category
                if category and metadata.get('category') != category:
                    continue
                
                assets.append(metadata)
            
            return assets
        except Exception as e:
            logger.error(f"Error listing assets: {str(e)}")
            return []
    
    async def import_asset_pack(self, zip_path: str) -> Dict[str, Any]:
        """
        Import assets from a zip file
        
        Args:
            zip_path: Path to zip file
            
        Returns:
            Import results
        """
        if not os.path.exists(zip_path):
            return {'status': 'error', 'error': 'Zip file not found'}
        
        try:
            imported = []
            errors = []
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to temp directory
                temp_dir = os.path.join(self.storage_path, 'temp', str(uuid.uuid4()))
                os.makedirs(temp_dir, exist_ok=True)
                
                # Check for manifest
                manifest = None
                if 'manifest.json' in zip_ref.namelist():
                    with zip_ref.open('manifest.json') as f:
                        manifest = json.load(f)
                
                # Extract all files
                zip_ref.extractall(temp_dir)
                
                # Import each file
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file == 'manifest.json':
                            continue
                        
                        file_path = os.path.join(root, file)
                        
                        # Get metadata from manifest if available
                        metadata = None
                        if manifest and file in manifest:
                            metadata = manifest[file]
                        
                        # Import asset
                        asset_id = await self.store_asset(file_path, metadata)
                        
                        if asset_id:
                            imported.append({
                                'asset_id': asset_id,
                                'filename': file,
                                'metadata': await self.get_asset_metadata(asset_id)
                            })
                        else:
                            errors.append({
                                'filename': file,
                                'error': 'Failed to import asset'
                            })
                
                # Clean up temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                'status': 'success',
                'imported_count': len(imported),
                'error_count': len(errors),
                'imported': imported,
                'errors': errors
            }
        except Exception as e:
            logger.error(f"Error importing asset pack: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def export_asset_pack(self, asset_ids: List[str], output_path: str) -> Dict[str, Any]:
        """
        Export assets to a zip file
        
        Args:
            asset_ids: List of asset IDs to export
            output_path: Path to output zip file
            
        Returns:
            Export results
        """
        try:
            exported = []
            errors = []
            manifest = {}
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for asset_id in asset_ids:
                    # Get asset metadata
                    metadata = await self.get_asset_metadata(asset_id)
                    if not metadata:
                        errors.append({
                            'asset_id': asset_id,
                            'error': 'Asset not found'
                        })
                        continue
                    
                    # Get asset path
                    asset_path = await self.get_asset_path(asset_id)
                    if not asset_path or not os.path.exists(asset_path):
                        errors.append({
                            'asset_id': asset_id,
                            'error': 'Asset file not found'
                        })
                        continue
                    
                    # Add to zip
                    filename = metadata.get('filename', f"{asset_id}.{metadata.get('extension', '')}")
                    zip_ref.write(asset_path, filename)
                    
                    # Add to manifest
                    manifest[filename] = metadata
                    
                    exported.append({
                        'asset_id': asset_id,
                        'filename': filename,
                        'metadata': metadata
                    })
                
                # Add manifest
                zip_ref.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            return {
                'status': 'success',
                'exported_count': len(exported),
                'error_count': len(errors),
                'exported': exported,
                'errors': errors,
                'output_path': output_path
            }
        except Exception as e:
            logger.error(f"Error exporting asset pack: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def search_assets(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search assets by name or metadata
        
        Args:
            query: Search query
            category: Filter by category
            
        Returns:
            List of matching asset metadata
        """
        assets = await self.list_assets(category)
        results = []
        
        query = query.lower()
        
        for asset in assets:
            # Check filename
            if query in asset.get('filename', '').lower():
                results.append(asset)
                continue
            
            # Check other metadata fields
            for key, value in asset.items():
                if isinstance(value, str) and query in value.lower():
                    results.append(asset)
                    break
        
        return results
    
    def _get_category(self, extension: str) -> str:
        """
        Get asset category from file extension
        
        Args:
            extension: File extension
            
        Returns:
            Asset category
        """
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return 'other'
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate MD5 hash of a file
        
        Args:
            file_path: Path to file
            
        Returns:
            MD5 hash as hexadecimal string
        """
        hash_md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
                
        return hash_md5.hexdigest()
    
    async def _store_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Store asset metadata in Redis
        
        Args:
            asset_id: Asset ID
            metadata: Asset metadata
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not await self.redis_bus.connect():
            logger.error("Cannot store asset metadata: Redis connection failed")
            return False
        
        key = f"{self.key_prefix}{asset_id}"
        
        try:
            # Store in Redis
            await self.redis_bus.redis.set(key, json.dumps(metadata))
            return True
        except Exception as e:
            logger.error(f"Error storing asset metadata: {str(e)}")
            return False
