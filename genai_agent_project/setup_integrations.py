#!/usr/bin/env python
"""
Utility to set up external integrations for GenAI Agent 3D
"""

import os
import sys
import yaml
import argparse
import subprocess
import shutil
from pathlib import Path

def check_integration(integration_name, path):
    """Check if an integration is available at the specified path"""
    if not path or not os.path.exists(path):
        print(f"[ERROR] {integration_name} path not found: {path}")
        return False
    
    if integration_name == "BlenderGPT":
        addon_path = os.path.join(path, 'blendergpt_addon.py')
        if not os.path.exists(addon_path):
            print(f"[ERROR] BlenderGPT addon not found at {addon_path}")
            return False
    
    elif integration_name == "Hunyuan-3D":
        main_script = os.path.join(path, 'run.py')
        if not os.path.exists(main_script):
            print(f"[ERROR] Hunyuan-3D main script not found at {main_script}")
            return False
    
    elif integration_name == "TRELLIS":
        init_file = os.path.join(path, 'trellis', '__init__.py')
        if not os.path.exists(init_file):
            print(f"[ERROR] TRELLIS module not found at {path}")
            return False
    
    print(f"[OK] {integration_name} found at {path}")
    return True

def update_config(config_path, updates):
    """Update the configuration file with the provided updates"""
    if not os.path.exists(config_path):
        print(f"[ERROR] Configuration file not found: {config_path}")
        return False
    
    # Read the configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Apply updates
    for section, section_updates in updates.items():
        if section not in config:
            config[section] = {}
        
        for key, value in section_updates.items():
            if key not in config[section]:
                config[section][key] = {}
                
            config[section][key].update(value)
    
    # Write back the updated configuration
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"[OK] Configuration updated: {config_path}")
    return True

def setup_blendergpt(args, config_path):
    """Set up BlenderGPT integration"""
    # Check if BlenderGPT is installed
    if not check_integration("BlenderGPT", args.blendergpt_path):
        return False
    
    # Check if Blender is installed
    if not os.path.exists(args.blender_path):
        print(f"[ERROR] Blender not found: {args.blender_path}")
        return False
    
    # Update configuration
    updates = {
        'integrations': {
            'blender_gpt': {
                'enabled': True,
                'blender_path': args.blender_path,
                'blendergpt_path': args.blendergpt_path,
                'api_key': args.api_key,
                'model': args.model or 'gpt-4'
            }
        },
        'tools': {
            'blender_gpt': {
                'enabled': True,
                'config': {
                    'blender_path': args.blender_path,
                    'blendergpt_path': args.blendergpt_path,
                    'api_key': args.api_key,
                    'model': args.model or 'gpt-4',
                    'output_dir': 'output/blendergpt/'
                }
            }
        }
    }
    
    return update_config(config_path, updates)

def setup_hunyuan3d(args, config_path):
    """Set up Hunyuan-3D integration"""
    # Check if Hunyuan-3D is installed
    if not check_integration("Hunyuan-3D", args.hunyuan_path):
        return False
    
    # Check if GPU is available if use_gpu is True
    if args.use_gpu:
        try:
            # Try to import torch to check CUDA availability
            import torch
            if not torch.cuda.is_available():
                print("[WARNING] CUDA is not available, but use_gpu is set to True")
                if not args.force:
                    print("Use --force to proceed anyway")
                    return False
        except ImportError:
            print("[WARNING] PyTorch is not installed, cannot check CUDA availability")
    
    # Update configuration
    updates = {
        'integrations': {
            'hunyuan_3d': {
                'enabled': True,
                'hunyuan_path': args.hunyuan_path,
                'use_gpu': args.use_gpu,
                'device': args.device or 'cuda:0',
                'output_dir': 'output/hunyuan/',
                'supported_formats': ['obj', 'glb', 'gltf', 'usdz']
            }
        },
        'tools': {
            'hunyuan_3d': {
                'enabled': True,
                'config': {
                    'hunyuan_path': args.hunyuan_path,
                    'use_gpu': args.use_gpu,
                    'device': args.device or 'cuda:0',
                    'output_dir': 'output/hunyuan/',
                    'supported_formats': ['obj', 'glb', 'gltf', 'usdz']
                }
            }
        }
    }
    
    return update_config(config_path, updates)

def setup_trellis(args, config_path):
    """Set up TRELLIS integration"""
    # Check if TRELLIS is installed
    if not check_integration("TRELLIS", args.trellis_path):
        return False
    
    # Update configuration
    updates = {
        'integrations': {
            'trellis': {
                'enabled': True,
                'trellis_path': args.trellis_path,
                'api_key': args.api_key,
                'model': args.model or 'gpt-4',
                'reasoning_examples_path': args.examples_path,
                'output_dir': 'output/trellis/'
            }
        },
        'tools': {
            'trellis': {
                'enabled': True,
                'config': {
                    'trellis_path': args.trellis_path,
                    'api_key': args.api_key,
                    'model': args.model or 'gpt-4',
                    'reasoning_examples_path': args.examples_path,
                    'output_dir': 'output/trellis/'
                }
            }
        }
    }
    
    return update_config(config_path, updates)

def main():
    parser = argparse.ArgumentParser(description='Set up external integrations for GenAI Agent 3D')
    
    # General arguments
    parser.add_argument('--config', default='config.yaml',
                        help='Path to configuration file (default: config.yaml)')
    parser.add_argument('--force', action='store_true',
                        help='Force setup even if checks fail')
    
    # Integration-specific subparsers
    subparsers = parser.add_subparsers(dest='integration',
                                       help='Integration to set up')
    
    # BlenderGPT
    blendergpt_parser = subparsers.add_parser('blendergpt',
                                             help='Set up BlenderGPT integration')
    blendergpt_parser.add_argument('--blendergpt-path', required=True,
                                 help='Path to BlenderGPT installation')
    blendergpt_parser.add_argument('--blender-path',
                                  default=r'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe',
                                  help='Path to Blender executable')
    blendergpt_parser.add_argument('--api-key',
                                  help='OpenAI API key')
    blendergpt_parser.add_argument('--model', default='gpt-4',
                                  help='Model to use (default: gpt-4)')
    
    # Hunyuan-3D
    hunyuan_parser = subparsers.add_parser('hunyuan3d',
                                          help='Set up Hunyuan-3D integration')
    hunyuan_parser.add_argument('--hunyuan-path', required=True,
                               help='Path to Hunyuan-3D installation')
    hunyuan_parser.add_argument('--use-gpu', action='store_true',
                               help='Use GPU for Hunyuan-3D')
    hunyuan_parser.add_argument('--device', default='cuda:0',
                               help='GPU device to use (default: cuda:0)')
    
    # TRELLIS
    trellis_parser = subparsers.add_parser('trellis',
                                          help='Set up TRELLIS integration')
    trellis_parser.add_argument('--trellis-path', required=True,
                               help='Path to TRELLIS installation')
    trellis_parser.add_argument('--api-key',
                               help='API key for language models')
    trellis_parser.add_argument('--model', default='gpt-4',
                               help='Model to use (default: gpt-4)')
    trellis_parser.add_argument('--examples-path',
                               help='Path to reasoning examples')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.integration:
        parser.print_help()
        return 1
    
    # Set up the selected integration
    if args.integration == 'blendergpt':
        success = setup_blendergpt(args, args.config)
    elif args.integration == 'hunyuan3d':
        success = setup_hunyuan3d(args, args.config)
    elif args.integration == 'trellis':
        success = setup_trellis(args, args.config)
    else:
        print(f"[ERROR] Unknown integration: {args.integration}")
        return 1
    
    if success:
        print(f"[SUCCESS] {args.integration} integration set up successfully")
        return 0
    else:
        print(f"[FAILURE] Failed to set up {args.integration} integration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
