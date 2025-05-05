"""
SVG Generator GUI

This script provides a graphical user interface for generating SVG diagrams
from natural language descriptions using various LLM providers.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import asyncio
import threading
import webbrowser
from pathlib import Path
import traceback

# Make sure the project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path")

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("svg_generator_gui.log")
    ]
)
logger = logging.getLogger("svg_generator_gui")

class AsyncTkApp:
    """Base class for Tkinter applications that need to run async code."""
    
    def __init__(self, loop=None):
        """Initialize with optional event loop."""
        self.loop = loop or asyncio.new_event_loop()
        self.root = None
    
    def run_async(self, coro):
        """Run an async coroutine from the Tkinter main thread."""
        if not self.loop.is_running():
            thread = threading.Thread(target=self._run_async_thread, args=(coro,), daemon=True)
            thread.start()
            return thread
        else:
            # If the loop is already running, schedule the coroutine
            return asyncio.run_coroutine_threadsafe(coro, self.loop)
    
    def _run_async_thread(self, coro):
        """Run the event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"Error in async thread: {e}")
            logger.error(traceback.format_exc())
    
    def start(self):
        """Start the Tkinter main loop."""
        if self.root:
            self.root.mainloop()
    
    def stop(self):
        """Stop the application and clean up."""
        if self.loop and self.loop.is_running():
            self.loop.stop()
        if self.root:
            self.root.quit()

class SVGGeneratorGUI(AsyncTkApp):
    """GUI for the SVG Generator."""
    
    def __init__(self):
        """Initialize the GUI."""
        super().__init__()
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("SVG Generator")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        # Set up variables
        self.provider_var = tk.StringVar(value="claude-direct")
        self.diagram_type_var = tk.StringVar(value="flowchart")
        self.description_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.status_var.set("Initializing...")
        
        # Set up the main UI
        self._create_widgets()
        self._create_layout()
        self._create_bindings()
        
        # Initialize providers and LLM services
        self.providers = []
        self.svg_content = None
        self.svg_path = None
        self.run_async(self._initialize_services())
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Create frame for input options
        self.options_frame = ttk.LabelFrame(self.root, text="Generation Options")
        
        # Provider selection
        self.provider_label = ttk.Label(self.options_frame, text="LLM Provider:")
        self.provider_combobox = ttk.Combobox(self.options_frame, 
                                             textvariable=self.provider_var,
                                             state="readonly")
        
        # Diagram type selection
        self.diagram_type_label = ttk.Label(self.options_frame, text="Diagram Type:")
        self.diagram_types = ["flowchart", "network", "sequence", "general"]
        self.diagram_type_combobox = ttk.Combobox(self.options_frame, 
                                                 textvariable=self.diagram_type_var,
                                                 values=self.diagram_types,
                                                 state="readonly")
        
        # Description input
        self.description_frame = ttk.LabelFrame(self.root, text="Diagram Description")
        self.description_text = scrolledtext.ScrolledText(self.description_frame, 
                                                         wrap=tk.WORD,
                                                         height=10)
        
        # Example descriptions
        self.examples_frame = ttk.LabelFrame(self.description_frame, text="Example Descriptions")
        
        self.flowchart_example_btn = ttk.Button(self.examples_frame, 
                                               text="Flowchart Example",
                                               command=lambda: self._insert_example("flowchart"))
        
        self.network_example_btn = ttk.Button(self.examples_frame, 
                                             text="Network Example",
                                             command=lambda: self._insert_example("network"))
        
        self.sequence_example_btn = ttk.Button(self.examples_frame, 
                                              text="Sequence Example",
                                              command=lambda: self._insert_example("sequence"))
        
        # Action buttons
        self.button_frame = ttk.Frame(self.root)
        
        self.generate_btn = ttk.Button(self.button_frame, 
                                      text="Generate SVG",
                                      command=self._generate_svg)
        
        self.view_btn = ttk.Button(self.button_frame, 
                                  text="View SVG",
                                  command=self._view_svg,
                                  state=tk.DISABLED)
        
        self.save_btn = ttk.Button(self.button_frame, 
                                  text="Save SVG As...",
                                  command=self._save_svg_as,
                                  state=tk.DISABLED)
        
        self.convert_btn = ttk.Button(self.button_frame, 
                                     text="Convert to 3D",
                                     command=self._convert_to_3d,
                                     state=tk.DISABLED)
        
        # Output and preview
        self.output_frame = ttk.LabelFrame(self.root, text="SVG Output")
        self.output_text = scrolledtext.ScrolledText(self.output_frame, 
                                                    wrap=tk.WORD,
                                                    height=15)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, 
                                   textvariable=self.status_var,
                                   relief=tk.SUNKEN,
                                   anchor=tk.W)
        
        # SVG Preview (using HTML)
        self.preview_frame = ttk.LabelFrame(self.root, text="SVG Preview")
        
        # Initialize preview canvas for SVG display
        self.preview_canvas = tk.Canvas(self.preview_frame, 
                                       background="white",
                                       highlightthickness=1,
                                       highlightbackground="lightgray")
        
        # Message when no SVG is available
        self.preview_message = ttk.Label(self.preview_canvas,
                                        text="Generate an SVG to see the preview",
                                        anchor=tk.CENTER)
    
    def _create_layout(self):
        """Create the layout for all widgets."""
        # Configure grid layout weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Options frame - fixed height
        self.root.rowconfigure(1, weight=1)  # Description frame - expands
        self.root.rowconfigure(2, weight=0)  # Button frame - fixed height
        self.root.rowconfigure(3, weight=1)  # Output frame - expands
        self.root.rowconfigure(4, weight=2)  # Preview frame - expands more
        self.root.rowconfigure(5, weight=0)  # Status bar - fixed height
        
        # Options frame
        self.options_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.options_frame.columnconfigure(1, weight=1)
        self.options_frame.columnconfigure(3, weight=1)
        
        self.provider_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.provider_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.diagram_type_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.diagram_type_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Description frame
        self.description_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.description_frame.columnconfigure(0, weight=1)
        self.description_frame.rowconfigure(0, weight=1)
        self.description_frame.rowconfigure(1, weight=0)
        
        self.description_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Examples frame
        self.examples_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.examples_frame.columnconfigure(0, weight=1)
        self.examples_frame.columnconfigure(1, weight=1)
        self.examples_frame.columnconfigure(2, weight=1)
        
        self.flowchart_example_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.network_example_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.sequence_example_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Button frame
        self.button_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)
        self.button_frame.columnconfigure(3, weight=1)
        
        self.generate_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.view_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.save_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.convert_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Output frame
        self.output_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(0, weight=1)
        
        self.output_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Preview frame
        self.preview_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.preview_frame.columnconfigure(0, weight=1)
        self.preview_frame.rowconfigure(0, weight=1)
        
        self.preview_canvas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.preview_message.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Status bar
        self.status_bar.grid(row=5, column=0, padx=0, pady=0, sticky="ew")
    
    def _create_bindings(self):
        """Create event bindings."""
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Update diagram type when selection changes
        self.diagram_type_combobox.bind("<<ComboboxSelected>>", self._on_diagram_type_changed)
    
    async def _initialize_services(self):
        """Initialize LLM services and update the UI."""
        try:
            # Import the LLM factory
            from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory
            
            # Get the LLM factory instance
            self.llm_factory = get_llm_factory()
            
            # Initialize the factory
            await self.llm_factory.initialize()
            
            # Get available providers
            providers = self.llm_factory.get_providers()
            self.providers = providers
            
            # Update UI on the main thread
            self.root.after(0, self._update_provider_ui, providers)
            
            # Check if 3D conversion is available
            self._check_3d_conversion()
            
            # Update status
            self.status_var.set("Ready")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            logger.error(traceback.format_exc())
            self.status_var.set(f"Error: {str(e)}")
    
    def _update_provider_ui(self, providers):
        """Update the UI with available providers."""
        # Extract provider IDs
        provider_ids = [p["id"] for p in providers]
        provider_names = {p["id"]: p["name"] for p in providers}
        
        # Update the combobox
        self.provider_combobox["values"] = provider_ids
        
        # Default to claude-direct if available, otherwise use the first provider
        if "claude-direct" in provider_ids:
            self.provider_var.set("claude-direct")
        elif provider_ids:
            self.provider_var.set(provider_ids[0])
    
    def _check_3d_conversion(self):
        """Check if 3D conversion is available."""
        try:
            # Try to import the SVG to 3D converter
            from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
            
            # Enable the convert button
            self.convert_btn.config(state=tk.NORMAL)
            logger.info("3D conversion is available")
            
            # Save the class for later use
            self.SVGTo3DConverter = SVGTo3DConverter
            
            return True
        except ImportError as e:
            logger.info(f"3D conversion is not available: {e}")
            
            # Add tooltip to the convert button
            tooltip = "3D conversion requires Blender's 'mathutils' module"
            self.convert_btn["state"] = tk.DISABLED
            
            return False
    
    def _insert_example(self, example_type):
        """Insert an example description based on the type."""
        examples = {
            "flowchart": """A detailed flowchart showing the process of online shopping from a user's perspective, including steps for browsing products, adding items to cart, checkout process, payment options, and order confirmation.""",
            
            "network": """A network diagram illustrating a secure enterprise network architecture with multiple security zones, including internet-facing DMZ, internal network segments, firewalls, load balancers, web servers, application servers, and database servers.""",
            
            "sequence": """A sequence diagram showing the authentication process for a web application, including the interactions between user, browser, authentication service, user database, and email notification system."""
        }
        
        # Clear and insert the example
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(tk.END, examples.get(example_type, ""))
        
        # Update the diagram type combobox
        self.diagram_type_var.set(example_type)
    
    def _on_diagram_type_changed(self, event):
        """Handle diagram type selection changes."""
        # Get the selected type
        diagram_type = self.diagram_type_var.get()
        
        # Suggest an example description
        if messagebox.askyesno("Use Example?", 
                              f"Would you like to use an example {diagram_type} description?"):
            self._insert_example(diagram_type)
    
    def _generate_svg(self):
        """Generate SVG from the description."""
        # Get inputs
        provider = self.provider_var.get()
        diagram_type = self.diagram_type_var.get()
        description = self.description_text.get(1.0, tk.END).strip()
        
        # Validate inputs
        if not description:
            messagebox.showerror("Input Error", "Please enter a diagram description")
            return
        
        # Update status
        self.status_var.set(f"Generating SVG with {provider}...")
        
        # Disable buttons during generation
        self.generate_btn.config(state=tk.DISABLED)
        
        # Start the generation in a separate thread
        self.run_async(self._run_svg_generation(provider, diagram_type, description))
    
    async def _run_svg_generation(self, provider, diagram_type, description):
        """Run the SVG generation in a separate thread."""
        try:
            # Generate SVG
            svg_content = await self.llm_factory.generate_svg(
                provider=provider,
                concept=description,
                style=diagram_type,
                temperature=0.4
            )
            
            # Save to the output directory
            output_dir = Path("output/svg")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate a filename
            filename = f"{provider.replace('-', '_')}_{diagram_type}_output.svg"
            output_path = output_dir / filename
            
            # Save the SVG
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            # Store the content and path
            self.svg_content = svg_content
            self.svg_path = output_path
            
            # Update the UI on the main thread
            self.root.after(0, self._update_ui_after_generation, svg_content, str(output_path))
            
        except Exception as e:
            logger.error(f"Error generating SVG: {e}")
            logger.error(traceback.format_exc())
            
            # Update status on the main thread
            self.root.after(0, self._update_ui_error, str(e))
    
    def _update_ui_after_generation(self, svg_content, output_path):
        """Update the UI after SVG generation."""
        # Enable buttons
        self.generate_btn.config(state=tk.NORMAL)
        self.view_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        
        # Update output text
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, svg_content)
        
        # Update status
        self.status_var.set(f"SVG generated and saved to {output_path}")
        
        # Update preview
        self._update_preview(svg_content)
        
        # Show success message
        messagebox.showinfo("Success", f"SVG generated and saved to {output_path}")
    
    def _update_ui_error(self, error_message):
        """Update the UI after an error."""
        # Enable generate button
        self.generate_btn.config(state=tk.NORMAL)
        
        # Update status
        self.status_var.set(f"Error: {error_message}")
        
        # Show error message
        messagebox.showerror("Error", f"Failed to generate SVG: {error_message}")
    
    def _update_preview(self, svg_content):
        """Update the SVG preview."""
        try:
            # Remove preview message
            self.preview_message.place_forget()
            
            # Save SVG to a temporary file for preview
            preview_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_preview.html")
            
            with open(preview_file, "w", encoding="utf-8") as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            background-color: white;
                        }}
                        svg {{
                            max-width: 100%;
                            max-height: 100vh;
                            border: 1px solid #ccc;
                        }}
                    </style>
                </head>
                <body>
                    {svg_content}
                </body>
                </html>
                """)
            
            # Create a label with instructions
            instructions = ttk.Label(
                self.preview_canvas,
                text="Preview available in your browser",
                anchor=tk.CENTER,
                background="white"
            )
            instructions.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            # Open the file in the default browser
            webbrowser.open(f"file://{preview_file}")
            
        except Exception as e:
            logger.error(f"Error updating preview: {e}")
            self.preview_message.config(text=f"Preview error: {str(e)}")
            self.preview_message.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def _view_svg(self):
        """View the generated SVG in the default browser."""
        if self.svg_path:
            # Convert to absolute path
            abs_path = os.path.abspath(self.svg_path)
            
            # Open in browser
            webbrowser.open(f"file://{abs_path}")
        else:
            messagebox.showinfo("No SVG", "Please generate an SVG first")
    
    def _save_svg_as(self):
        """Save the SVG to a user-specified location."""
        if not self.svg_content:
            messagebox.showinfo("No SVG", "Please generate an SVG first")
            return
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.svg_path) if self.svg_path else "."
        )
        
        if file_path:
            try:
                # Save the SVG
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.svg_content)
                
                # Update status
                self.status_var.set(f"SVG saved to {file_path}")
                
                # Show success message
                messagebox.showinfo("Success", f"SVG saved to {file_path}")
                
            except Exception as e:
                logger.error(f"Error saving SVG: {e}")
                messagebox.showerror("Error", f"Failed to save SVG: {str(e)}")
    
    def _convert_to_3d(self):
        """Convert the SVG to a 3D model."""
        if not self.svg_path:
            messagebox.showinfo("No SVG", "Please generate an SVG first")
            return
        
        try:
            # Check if 3D conversion is available
            if not hasattr(self, "SVGTo3DConverter"):
                messagebox.showerror("Not Available", 
                                    "3D conversion is not available.\nBlender's 'mathutils' module is required.")
                return
            
            # Ask for save location
            output_dir = Path("output/models")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            svg_filename = os.path.basename(self.svg_path)
            model_filename = svg_filename.replace(".svg", ".blend")
            output_path = output_dir / model_filename
            
            # Update status
            self.status_var.set(f"Converting SVG to 3D model...")
            
            # Disable the button during conversion
            self.convert_btn.config(state=tk.DISABLED)
            
            # Start the conversion in a separate thread
            self.run_async(self._run_3d_conversion(str(self.svg_path), str(output_path)))
            
        except Exception as e:
            logger.error(f"Error in 3D conversion: {e}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to convert to 3D: {str(e)}")
            self.convert_btn.config(state=tk.NORMAL)
    
    async def _run_3d_conversion(self, svg_path, output_path):
        """Run the 3D conversion in a separate thread."""
        try:
            # Initialize the converter
            converter = self.SVGTo3DConverter(debug=True)
            
            # Convert SVG to 3D
            result = await converter.convert_svg_to_3d(
                svg_path=svg_path,
                output_path=output_path
            )
            
            # Update the UI on the main thread
            self.root.after(0, self._update_ui_after_conversion, result, output_path)
            
        except Exception as e:
            logger.error(f"Error in 3D conversion: {e}")
            logger.error(traceback.format_exc())
            
            # Update status on the main thread
            self.root.after(0, self._update_ui_error_conversion, str(e))
    
    def _update_ui_after_conversion(self, result, output_path):
        """Update the UI after 3D conversion."""
        # Enable button
        self.convert_btn.config(state=tk.NORMAL)
        
        if result:
            # Update status
            self.status_var.set(f"SVG converted to 3D model: {output_path}")
            
            # Show success message
            messagebox.showinfo("Success", f"SVG converted to 3D model:\n{output_path}")
        else:
            # Update status
            self.status_var.set("Failed to convert SVG to 3D model")
            
            # Show error message
            messagebox.showerror("Error", "Failed to convert SVG to 3D model")
    
    def _update_ui_error_conversion(self, error_message):
        """Update the UI after a conversion error."""
        # Enable button
        self.convert_btn.config(state=tk.NORMAL)
        
        # Update status
        self.status_var.set(f"Conversion error: {error_message}")
        
        # Show error message
        messagebox.showerror("Conversion Error", f"Failed to convert to 3D: {error_message}")

def main():
    """Main entry point for the application."""
    app = SVGGeneratorGUI()
    app.start()

if __name__ == "__main__":
    main()
