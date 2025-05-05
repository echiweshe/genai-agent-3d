"""
Simple script to view SVG files in the default browser.
"""

import os
import sys
import webbrowser
import argparse
from pathlib import Path

def view_svg(file_path):
    """
    Open an SVG file in the default web browser.
    
    Args:
        file_path: Path to SVG file
    """
    # Get absolute path
    abs_path = os.path.abspath(file_path)
    
    # Check if file exists
    if not os.path.exists(abs_path):
        print(f"Error: File '{abs_path}' does not exist.")
        return False
    
    # Check if file is an SVG
    if not abs_path.lower().endswith('.svg'):
        print(f"Error: File '{abs_path}' is not an SVG file.")
        return False
    
    # Open in browser
    print(f"Opening SVG file: {abs_path}")
    webbrowser.open('file://' + abs_path)
    return True

def list_svg_files(directory="output/svg"):
    """
    List all SVG files in the specified directory.
    
    Args:
        directory: Directory to search for SVG files
    """
    # Get absolute path
    abs_path = os.path.abspath(directory)
    
    # Check if directory exists
    if not os.path.exists(abs_path):
        print(f"Error: Directory '{abs_path}' does not exist.")
        return []
    
    # List SVG files
    svg_files = []
    for file in os.listdir(abs_path):
        if file.lower().endswith('.svg'):
            svg_files.append(os.path.join(abs_path, file))
    
    return svg_files

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="View SVG files in the default browser.")
    parser.add_argument("--file", "-f", type=str, default=None,
                       help="SVG file to view")
    parser.add_argument("--latest", "-l", action="store_true",
                       help="View the latest SVG file")
    parser.add_argument("--list", action="store_true",
                       help="List all SVG files")
    parser.add_argument("--directory", "-d", type=str, default="output/svg",
                       help="Directory containing SVG files")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # List all SVG files
    if args.list:
        svg_files = list_svg_files(args.directory)
        if svg_files:
            print(f"Found {len(svg_files)} SVG files:")
            for i, file in enumerate(svg_files):
                print(f"  {i+1}. {os.path.basename(file)}")
        else:
            print(f"No SVG files found in '{args.directory}'.")
        sys.exit(0)
    
    # View the latest SVG file
    if args.latest:
        svg_files = list_svg_files(args.directory)
        if svg_files:
            # Sort by modification time (newest first)
            svg_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            latest_file = svg_files[0]
            print(f"Opening latest SVG file: {os.path.basename(latest_file)}")
            view_svg(latest_file)
        else:
            print(f"No SVG files found in '{args.directory}'.")
        sys.exit(0)
    
    # View specified file
    if args.file:
        view_svg(args.file)
    else:
        print("Please specify an SVG file to view with --file or use --latest to view the latest SVG file.")
        print("Use --list to see all available SVG files.")
