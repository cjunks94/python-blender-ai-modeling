"""Main application window using Tkinter."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional
from pathlib import Path


class MainWindow:
    """Main application window for Blender AI Modeling."""
    
    def __init__(self):
        """Initialize the main window."""
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("Python Blender AI Modeling")
        self.root.geometry("800x600")
        
        # Initialize UI components
        self._setup_menu()
        self._setup_main_frame()
        
        self.logger.info("Main window initialized")
    
    def _setup_menu(self) -> None:
        """Set up the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(label="Open Project", command=self._open_project)
        file_menu.add_command(label="Save Project", command=self._save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_application)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_main_frame(self) -> None:
        """Set up the main application frame."""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Python Blender AI Modeling", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Object creation section
        object_frame = ttk.LabelFrame(main_frame, text="Create 3D Object", padding="10")
        object_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        object_frame.columnconfigure(1, weight=1)
        
        # Object type selection
        ttk.Label(object_frame, text="Object Type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.object_type = tk.StringVar(value="cube")
        object_combo = ttk.Combobox(
            object_frame, 
            textvariable=self.object_type,
            values=["cube", "sphere", "cylinder", "plane"],
            state="readonly"
        )
        object_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Size parameter
        ttk.Label(object_frame, text="Size:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.size_var = tk.DoubleVar(value=2.0)
        size_scale = ttk.Scale(
            object_frame,
            from_=0.1,
            to=10.0,
            variable=self.size_var,
            orient="horizontal"
        )
        size_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Size value display
        self.size_label = ttk.Label(object_frame, text="2.0")
        self.size_label.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        self.size_var.trace("w", self._update_size_label)
        
        # Generate button
        generate_btn = ttk.Button(
            object_frame,
            text="Generate Model",
            command=self._generate_model
        )
        generate_btn.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # Status text area
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        status_frame.rowconfigure(0, weight=1)
        
        # Add initial status message
        self._add_status_message("Application initialized. Ready to create 3D models.")
    
    def _update_size_label(self, *args) -> None:
        """Update the size value display."""
        self.size_label.config(text=f"{self.size_var.get():.1f}")
    
    def _add_status_message(self, message: str) -> None:
        """Add a message to the status text area."""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def _generate_model(self) -> None:
        """Generate a 3D model based on current settings."""
        object_type = self.object_type.get()
        size = self.size_var.get()
        
        self._add_status_message(f"Generating {object_type} with size {size:.1f}...")
        
        try:
            # TODO: Implement actual Blender integration
            # For now, just show a placeholder message
            self._add_status_message("Model generation not yet implemented.")
            self._add_status_message("This will integrate with Blender via subprocess.")
            
            messagebox.showinfo(
                "Coming Soon",
                f"Model generation will create a {object_type} with size {size:.1f}\n\n"
                "This feature will be implemented in the next development phase."
            )
            
        except Exception as e:
            error_msg = f"Error generating model: {e}"
            self.logger.error(error_msg)
            self._add_status_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def _new_project(self) -> None:
        """Create a new project."""
        self._add_status_message("New project created.")
    
    def _open_project(self) -> None:
        """Open an existing project."""
        filename = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self._add_status_message(f"Opened project: {filename}")
    
    def _save_project(self) -> None:
        """Save the current project."""
        filename = filedialog.asksaveasfilename(
            title="Save Project",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self._add_status_message(f"Saved project: {filename}")
    
    def _exit_application(self) -> None:
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()
    
    def _show_about(self) -> None:
        """Show the about dialog."""
        messagebox.showinfo(
            "About",
            "Python Blender AI Modeling v0.1.0\n\n"
            "A desktop application for creating 3D models using Blender\n"
            "programmatically with AI integration.\n\n"
            "Built with Python and Tkinter."
        )
    
    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Application error: {e}", exc_info=True)
            raise