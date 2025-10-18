"""
EnergyPlus Concurrent Simulation Explorer - UI Design Mockup
This is a design prototype to establish the interface layout before full implementation.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class SimulationExplorerUI:
    """UI mockup for the EnergyPlus concurrent simulation explorer"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EnergyPlus Concurrent Simulation Explorer")
        self.root.geometry("1200x800")
        
        # Data parameters
        self.thread_counts = [1, 2, 4, 8, 16, 32]  # Rows
        self.concurrent_sims = [1, 2, 4, 8, 16, 32, 64]  # Columns
        
        # UI state
        self.baseline_selection = (0, 0)  # Default: 1 thread, 1 sim
        self.baseline_mode = tk.StringVar(value="single")  # "single", "row", "column"
        self.dataset_selections = {}  # Will track checkbox states
        self.selected_functions = set()  # Track selected functions in chart
        self.show_stats_panel = tk.BooleanVar(value=True)  # Show/hide stats panel
        self.show_function_labels = tk.BooleanVar(value=True)  # Show/hide function labels
        
        # Baseline selection variables for different modes
        self.single_baseline_var = tk.StringVar()  # For single dataset baseline
        self.row_baseline_var = tk.StringVar()     # For row baseline
        self.column_baseline_var = tk.StringVar()  # For column baseline
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the main UI layout with resizable panels"""
        
        # Configure root window for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main horizontal paned window for resizable panels
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Left panel: Chart and data matrix (will be further divided vertically)
        left_panel = ttk.Frame(main_paned)
        main_paned.add(left_panel, weight=3)  # Takes 3/4 of horizontal space initially
        
        # Create vertical paned window for chart and data matrix
        vertical_paned = ttk.PanedWindow(left_panel, orient=tk.VERTICAL)
        vertical_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Top section: Chart display area
        chart_panel = ttk.Frame(vertical_paned)
        vertical_paned.add(chart_panel, weight=3)  # Takes 3/4 of vertical space initially
        self.create_chart_area(chart_panel)
        
        # Bottom section: Dataset selection table
        table_panel = ttk.Frame(vertical_paned)
        vertical_paned.add(table_panel, weight=1)  # Takes 1/4 of vertical space initially
        self.create_selection_table(table_panel)
        
        # Right panel: Statistics panel
        stats_panel = ttk.Frame(main_paned)
        main_paned.add(stats_panel, weight=1)  # Takes 1/4 of horizontal space initially
        self.create_statistics_panel(stats_panel)
        
        # Initialize with some default selections
        self.initialize_defaults()
    
    def create_chart_area(self, parent):
        """Create the matplotlib chart display area with function selection"""
        
        # Configure parent for expansion
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Chart frame
        chart_frame = ttk.LabelFrame(parent, text="Performance Comparison Chart (Click bars to select functions)", padding="5")
        chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        
        # Create matplotlib figure with minimal margins
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)  # Minimize whitespace
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Connect click and hover events
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_chart_hover)
        
        # Create hover annotation (initially hidden)
        self.hover_annotation = self.ax.annotate('', xy=(0,0), xytext=(20,20), 
                                               textcoords="offset points",
                                               bbox=dict(boxstyle="round", fc="yellow", alpha=0.8),
                                               arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                                               visible=False)
        
        # Create a demo chart
        self.create_demo_chart()
    
    def create_selection_table(self, parent):
        """Create the dataset selection table with scrollbar"""
        
        # Configure parent for expansion
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Selection frame
        selection_frame = ttk.LabelFrame(parent, text="Dataset Selection Matrix", padding="5")
        selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        selection_frame.grid_rowconfigure(1, weight=1)
        selection_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions
        instructions = ttk.Label(selection_frame, 
                               text="Select datasets to overlay (checkboxes) and baseline reference (radio button):")
        instructions.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Create scrollable frame for the table
        canvas = tk.Canvas(selection_frame, height=200)
        scrollbar = ttk.Scrollbar(selection_frame, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Create table header in scrollable frame
        self.create_table_header(self.scrollable_frame)
        
        # Create table rows in scrollable frame
        self.create_table_rows(self.scrollable_frame)
        
        # Control buttons in main selection frame (not scrollable)
        self.create_control_buttons(selection_frame)
    
    def create_table_header(self, parent):
        """Create the table header with 21 columns (3 per sim) and spanning headers"""
        
        # Create a frame for the entire table
        self.table_frame = ttk.Frame(parent)
        self.table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid: 1 corner + 21 columns (3 per sim)
        total_cols = 1 + (len(self.concurrent_sims) * 3)  # 1 + 21 = 22 columns
        for i in range(total_cols):
            self.table_frame.grid_columnconfigure(i, weight=0, minsize=50)
        
        # Corner cell
        corner_label = ttk.Label(self.table_frame, text="Threads", 
                                font=('TkDefaultFont', 9, 'bold'),
                                relief='solid', borderwidth=1)
        corner_label.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Column headers spanning 3 columns each
        self.column_baseline_radios = []
        for sim_idx, sims in enumerate(self.concurrent_sims):
            start_col = 1 + (sim_idx * 3)  # Start column for this sim group
            
            # Spanning header for sim count
            sim_header = ttk.Label(self.table_frame, text=f"{sims} Sim", 
                                  font=('TkDefaultFont', 9, 'bold'),
                                  relief='solid', borderwidth=1)
            sim_header.grid(row=0, column=start_col, columnspan=3, sticky=(tk.W, tk.E))
            
            # Sub-headers for the 3 columns
            time_header = ttk.Label(self.table_frame, text="Time", 
                                   font=('TkDefaultFont', 8),
                                   relief='solid', borderwidth=1)
            time_header.grid(row=1, column=start_col, sticky=(tk.W, tk.E))
            
            check_header = ttk.Label(self.table_frame, text="☑", 
                                    font=('TkDefaultFont', 8),
                                    relief='solid', borderwidth=1)
            check_header.grid(row=1, column=start_col + 1, sticky=(tk.W, tk.E))
            
            radio_header = ttk.Label(self.table_frame, text="Base", 
                                    font=('TkDefaultFont', 8),
                                    relief='solid', borderwidth=1)
            radio_header.grid(row=1, column=start_col + 2, sticky=(tk.W, tk.E))
            
            # Column baseline radio button (for column mode)
            rb_col = ttk.Radiobutton(sim_header, text="□", 
                                   variable=self.column_baseline_var, value=str(sim_idx),
                                   command=lambda c=sim_idx: self.on_column_baseline_change(c))
            # Position it in the header but don't pack yet - visibility controlled later
            self.column_baseline_radios.append(rb_col)
    
    def create_table_rows(self, parent):
        """Create the table rows with 21 columns (3 per sim): time, checkbox, radio"""
        
        # Initialize baseline selection variables  
        self.single_baseline_var.set("0_0")  # Default to first row, first column
        self.row_baseline_var.set("0")       # Default to first row
        self.column_baseline_var.set("0")    # Default to first column
        
        # Store radio button widgets for visibility control
        self.row_baseline_radios = []
        self.single_baseline_radios = []
        
        for row_idx, threads in enumerate(self.thread_counts):
            table_row = row_idx + 2  # Start after header rows (0 and 1)
            
            # Row header with thread count and row baseline control
            row_header = ttk.Label(self.table_frame, text=f"{threads}",
                                  font=('TkDefaultFont', 9, 'bold'),
                                  relief='solid', borderwidth=1)
            row_header.grid(row=table_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Row baseline radio button (for row mode). Note remove text
            rb_row = ttk.Radiobutton(row_header, text="",
                                   variable=self.row_baseline_var, value=str(row_idx),
                                   command=lambda r=row_idx: self.on_row_baseline_change(r))
            self.row_baseline_radios.append(rb_row)
            
            # Create 3 columns for each sim count
            for sim_idx, sims in enumerate(self.concurrent_sims):
                start_col = 1 + (sim_idx * 3)
                
                # Column 1: Execution time (white text)
                exec_time = self.get_mock_execution_time(threads, sims)
                time_label = ttk.Label(self.table_frame, text=f"{exec_time:.1f}s",
                                     font=('TkDefaultFont', 9), foreground='white',
                                     background='black', relief='solid', borderwidth=1)
                time_label.grid(row=table_row, column=start_col, sticky=(tk.W, tk.E, tk.N, tk.S))
                
                # Column 2: Dataset checkbox
                var = tk.BooleanVar()
                self.dataset_selections[(row_idx, sim_idx)] = var
                cb_frame = ttk.Label(self.table_frame, relief='solid', borderwidth=1)
                cb_frame.grid(row=table_row, column=start_col + 1, sticky=(tk.W, tk.E, tk.N, tk.S))
                cb = ttk.Checkbutton(cb_frame, variable=var,
                                   command=lambda r=row_idx, c=sim_idx: self.on_selection_change(r, c))
                cb.pack(anchor=tk.CENTER)
                
                # Column 3: Single baseline radio button
                radio_value = f"{row_idx}_{sim_idx}"
                rb_frame = ttk.Label(self.table_frame, relief='solid', borderwidth=1)
                rb_frame.grid(row=table_row, column=start_col + 2, sticky=(tk.W, tk.E, tk.N, tk.S))
                # Removed text
                rb_single = ttk.Radiobutton(rb_frame, text="",
                                          variable=self.single_baseline_var, value=radio_value,
                                          command=lambda r=row_idx, c=sim_idx: self.on_single_baseline_change(r, c))
                rb_single.pack(anchor=tk.CENTER)
                self.single_baseline_radios.append(rb_single)
        
        # Set initial visibility based on default mode
        self.update_radio_visibility()
    
    def create_control_buttons(self, parent):
        """Create control buttons below the table"""
        
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, pady=(10, 0), sticky=tk.W)
        
        # Update chart button
        ttk.Button(button_frame, text="Update Chart", 
                  command=self.update_chart).pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear all selections
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_selections).pack(side=tk.LEFT, padx=(0, 10))
        
        # Select row (for quick selection of all sims for a thread count)
        ttk.Button(button_frame, text="Select Row", 
                  command=self.select_current_row).pack(side=tk.LEFT, padx=(0, 10))
        
        # Select column (for quick selection of all threads for a sim count)
        ttk.Button(button_frame, text="Select Column", 
                  command=self.select_current_column).pack(side=tk.LEFT, padx=(0, 10))
        
        # Toggle stats panel
        ttk.Checkbutton(button_frame, text="Show Statistics", variable=self.show_stats_panel,
                       command=self.toggle_stats_panel).pack(side=tk.LEFT, padx=(0, 10))
        
        # Toggle function labels
        ttk.Checkbutton(button_frame, text="Show Function Labels", variable=self.show_function_labels,
                       command=self.update_chart).pack(side=tk.LEFT, padx=(0, 10))
        
        # Baseline comparison mode
        baseline_frame = ttk.LabelFrame(button_frame, text="Baseline Mode", padding="2")
        baseline_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Radiobutton(baseline_frame, text="Single", variable=self.baseline_mode, value="single",
                       command=self.update_comparison_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(baseline_frame, text="Row", variable=self.baseline_mode, value="row",
                       command=self.update_comparison_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(baseline_frame, text="Column", variable=self.baseline_mode, value="column",
                       command=self.update_comparison_mode).pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="Ready")
        self.status_label.pack(side=tk.RIGHT)
    
    def create_demo_chart(self):
        """Create a demo chart to show the concept"""
        
        # Demo data for visualization concept
        functions = ['Function A', 'Function B', 'Function C', 'Function D', 'Function E']
        
        # Simulate different performance ratios for overlaid datasets
        datasets = [
            {'name': '1 sim, 1 thread', 'ratios': [1.0, 1.0, 1.0, 1.0, 1.0], 'alpha': 0.7},
            {'name': '2 sims, 2 threads', 'ratios': [1.2, 0.8, 1.1, 0.9, 1.3], 'alpha': 0.7},
            {'name': '4 sims, 4 threads', 'ratios': [1.8, 0.6, 1.5, 0.7, 2.1], 'alpha': 0.7},
        ]
        
        self.ax.clear()
        
        # Plot overlaid bars for each dataset
        bar_width = 0.8
        x = np.arange(len(functions))
        
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']
        
        for i, dataset in enumerate(datasets):
            self.ax.bar(x, dataset['ratios'], bar_width, 
                       alpha=dataset['alpha'], 
                       color=colors[i % len(colors)],
                       label=dataset['name'])
        
        # Add baseline reference line
        self.ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.8, linewidth=2)
        
        # Formatting with conditional function labels
        self.ax.set_ylabel('Performance Ratio (Normalized to Baseline)')
        self.ax.set_title('Overlaid Performance Comparison - Demo Chart')
        self.ax.set_xticks(x)
        
        # Toggle function labels based on user preference
        if self.show_function_labels.get():
            self.ax.set_xticklabels(functions)
            self.ax.set_xlabel('Functions')
            # Adjust bottom margin when labels are shown
            self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15)
        else:
            self.ax.set_xticklabels([''] * len(functions))  # Hide labels
            self.ax.set_xlabel('')
            # Reduce bottom margin when labels are hidden
            self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.05)
        
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Store function names for hover functionality
        self.function_names = functions
        self.dataset_names = [d['name'] for d in datasets]
        
        self.canvas.draw()
    
    def create_statistics_panel(self, parent):
        """Create the statistics panel on the right side"""
        
        # Configure parent for expansion
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        self.stats_frame = ttk.LabelFrame(parent, text="Statistics Panel", padding="5")
        self.stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stats_frame.grid_rowconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollable text widget for statistics
        stats_container = ttk.Frame(self.stats_frame)
        stats_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_container.grid_rowconfigure(0, weight=1)
        stats_container.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbar
        self.stats_text = tk.Text(stats_container, wrap=tk.WORD, width=30, height=20)
        scrollbar = ttk.Scrollbar(stats_container, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Initialize with default stats
        self.update_statistics()
    
    def on_chart_click(self, event):
        """Handle clicks on chart bars to select/deselect functions"""
        if event.inaxes != self.ax:
            return
        
        # Mock function selection - in real implementation, detect which bar was clicked
        if event.xdata is not None:
            func_index = int(round(event.xdata))
            if 0 <= func_index < 5:  # Demo has 5 functions
                func_name = f"Function {chr(65 + func_index)}"  # A, B, C, D, E
                
                if func_name in self.selected_functions:
                    self.selected_functions.remove(func_name)
                    print(f"Deselected function: {func_name}")
                else:
                    self.selected_functions.add(func_name)
                    print(f"Selected function: {func_name}")
                
                self.update_statistics()
                self.highlight_selected_functions()
    
    def on_chart_hover(self, event):
        """Handle mouse hover over chart to show function/dataset info"""
        if event.inaxes != self.ax:
            self.hover_annotation.set_visible(False)
            self.canvas.draw_idle()
            return
        
        # Check if mouse is over a bar
        if event.xdata is not None and event.ydata is not None:
            func_index = int(round(event.xdata))
            if 0 <= func_index < len(self.function_names):
                func_name = self.function_names[func_index]
                
                # Determine which dataset based on y-value and overlaid bars
                # For demo, we'll show the highest dataset at this x position
                y_value = event.ydata
                hover_text = f"Function: {func_name}\nRatio: {y_value:.2f}x\nDataset: Estimated"
                
                self.hover_annotation.xy = (event.xdata, event.ydata)
                self.hover_annotation.set_text(hover_text)
                self.hover_annotation.set_visible(True)
                self.canvas.draw_idle()
            else:
                self.hover_annotation.set_visible(False)
                self.canvas.draw_idle()
        else:
            self.hover_annotation.set_visible(False)
            self.canvas.draw_idle()
    
    def update_comparison_mode(self):
        """Update comparison logic based on baseline mode"""
        mode = self.baseline_mode.get()
        
        # Update radio button visibility first
        self.update_radio_visibility()
        
        # Get baseline information based on current mode
        if mode == "single":
            baseline_key = self.single_baseline_var.get()
            if baseline_key and '_' in baseline_key:
                baseline_row, baseline_col = map(int, baseline_key.split('_'))
            else:
                baseline_row, baseline_col = 0, 0
        elif mode == "row":
            baseline_row = int(self.row_baseline_var.get()) if self.row_baseline_var.get() else 0
            baseline_col = 0  # Not relevant for row mode
        elif mode == "column":
            baseline_col = int(self.column_baseline_var.get()) if self.column_baseline_var.get() else 0
            baseline_row = 0  # Not relevant for column mode
        else:
            baseline_row, baseline_col = 0, 0
        
        # Clear current selections
        for var in self.dataset_selections.values():
            var.set(False)
        
        if mode == "single":
            # Compare all datasets to the single selected baseline
            pass  # No auto-selection needed
        elif mode == "row":
            # Select all datasets in the baseline row (same thread count)
            for col in range(len(self.concurrent_sims)):
                self.dataset_selections[(baseline_row, col)].set(True)
        elif mode == "column":
            # Select all datasets in the baseline column (same sim count)
            for row in range(len(self.thread_counts)):
                self.dataset_selections[(row, baseline_col)].set(True)
        
        self.update_status()
        self.update_statistics()
    
    def update_chart(self):
        """Refresh the chart display with current settings"""
        self.create_demo_chart()
    
    def clear_selections(self):
        """Clear all dataset selections"""
        for var in self.dataset_selections.values():
            var.set(False)
        self.update_status()
        self.update_statistics()
    
    def highlight_selected_functions(self):
        """Visual feedback for selected functions"""
        # In real implementation, would highlight selected bars
        selected_list = list(self.selected_functions)
        print(f"Currently selected functions: {selected_list}")
    
    def update_statistics(self):
        """Update the statistics panel based on selections"""
        self.stats_text.delete(1.0, tk.END)
        
        selected_datasets = sum(1 for var in self.dataset_selections.values() if var.get())
        baseline_mode = self.baseline_mode.get()
        
        # Get baseline information based on current mode
        if baseline_mode == "single":
            baseline_key = self.single_baseline_var.get()
            if baseline_key and '_' in baseline_key:
                baseline_row, baseline_col = map(int, baseline_key.split('_'))
                baseline_threads = self.thread_counts[baseline_row]
                baseline_sims = self.concurrent_sims[baseline_col]
            else:
                baseline_threads, baseline_sims = 1, 1
        elif baseline_mode == "row":
            baseline_row = int(self.row_baseline_var.get()) if self.row_baseline_var.get() else 0
            baseline_threads = self.thread_counts[baseline_row]
            baseline_sims = "Variable"
        elif baseline_mode == "column":
            baseline_col = int(self.column_baseline_var.get()) if self.column_baseline_var.get() else 0
            baseline_sims = self.concurrent_sims[baseline_col]
            baseline_threads = "Variable"
        else:
            baseline_threads, baseline_sims = 1, 1
        
        stats_text = f"PERFORMANCE ANALYSIS\n{'='*25}\n\n"
        stats_text += f"Selected Datasets: {selected_datasets}\n"
        stats_text += f"Baseline: {baseline_threads} threads, {baseline_sims} sims\n"
        stats_text += f"Comparison Mode: {baseline_mode.capitalize()}\n\n"
        
        # Explain comparison mode
        if baseline_mode == "single":
            stats_text += "Mode: All datasets compared to single baseline\n\n"
        elif baseline_mode == "row":
            stats_text += "Mode: Datasets compared within same row\n"
            stats_text += "(Same thread count, different sim counts)\n\n"
        elif baseline_mode == "column":
            stats_text += "Mode: Datasets compared within same column\n"
            stats_text += "(Same sim count, different thread counts)\n\n"
        
        if len(self.selected_functions) > 0:
            stats_text += f"SELECTED FUNCTIONS\n{'-'*20}\n"
            for func in sorted(self.selected_functions):
                stats_text += f"• {func}\n"
            stats_text += "\n"
        
        if selected_datasets == 1:
            stats_text += "SINGLE DATASET ANALYSIS\n"
            stats_text += "-" * 25 + "\n"
            stats_text += "Dataset Context:\n"
            stats_text += "• Total simulation time: 156.1s\n"
            stats_text += "• Performance ratio: 0.40x\n"
            stats_text += "• Memory usage: 2.1 GB\n"
            stats_text += "• CPU utilization: 95%\n"
            stats_text += "• Resource contention: Low\n\n"
            
            if self.selected_functions:
                stats_text += "Function-Specific Metrics:\n"
                for func in sorted(self.selected_functions):
                    stats_text += f"• {func}: 1.2x baseline\n"
            
        elif selected_datasets > 1:
            stats_text += "MULTI-DATASET COMPARISON\n"
            stats_text += "-" * 27 + "\n"
            stats_text += "Performance Statistics:\n"
            stats_text += "• Best performance: 0.40x (8 threads, 1 sim)\n"
            stats_text += "• Worst performance: 2.73x (1 thread, 8 sims)\n"
            stats_text += "• Average performance: 1.15x\n"
            stats_text += "• Standard deviation: 0.89x\n\n"
            
            stats_text += "Threading Effects:\n"
            stats_text += "• Optimal thread count: 8-16\n"
            stats_text += "• Diminishing returns: >16 threads\n"
            stats_text += "• Context switching penalty: High at 32 threads\n\n"
            
            stats_text += "Concurrency Effects:\n"
            stats_text += "• Resource contention starts: >4 sims\n"
            stats_text += "• Memory pressure: Severe at >16 sims\n"
            stats_text += "• I/O bottlenecks: Critical at >32 sims\n\n"
            
            if self.selected_functions:
                stats_text += "Function Performance Ranges:\n"
                for func in sorted(self.selected_functions):
                    stats_text += f"• {func}: 0.6x - 2.8x range\n"
        
        else:
            stats_text += "No datasets selected.\n"
            stats_text += "Select datasets from the matrix below to see analysis."
        
        self.stats_text.insert(1.0, stats_text)
    
    def toggle_stats_panel(self):
        """Show/hide the statistics panel"""
        if self.show_stats_panel.get():
            self.stats_frame.grid()
        else:
            self.stats_frame.grid_remove()
    
    def select_current_column(self):
        """Select all datasets in a column (same sim count, different threads)"""
        # For demo, select first column
        for row in range(len(self.thread_counts)):
            self.dataset_selections[(row, 0)].set(True)
        self.update_status()
    
    def initialize_defaults(self):
        """Set some default selections for demonstration"""
        
        # Select a few datasets by default
        self.dataset_selections[(0, 0)].set(True)  # 1 sim, 1 thread
        self.dataset_selections[(1, 1)].set(True)  # 2 sims, 2 threads
        self.dataset_selections[(2, 2)].set(True)  # 4 sims, 4 threads
        
        self.update_status()
    
    def on_selection_change(self, row, col):
        """Handle checkbox selection changes"""
        self.update_status()
        print(f"Selection changed: {self.concurrent_sims[row]} sims, {self.thread_counts[col]} threads")
    
    def on_baseline_change(self, row):
        """Handle baseline selection changes"""
        self.baseline_selection = (row, 0)  # For now, assume first thread count
        self.update_status()
        print(f"Baseline changed to: {self.concurrent_sims[row]} sims")
    
    def update_chart(self):
        """Update the chart based on current selections"""
        selected_count = sum(1 for var in self.dataset_selections.values() if var.get())
        print(f"Updating chart with {selected_count} selected datasets")
        self.status_label.config(text=f"Chart updated with {selected_count} datasets")
    
    def clear_selections(self):
        """Clear all checkbox selections"""
        for var in self.dataset_selections.values():
            var.set(False)
        self.update_status()
    
    def select_current_row(self):
        """Select all datasets in the current baseline row"""
        mode = self.baseline_mode.get()
        if mode == "single":
            baseline_key = self.single_baseline_var.get()
            if baseline_key and '_' in baseline_key:
                baseline_row = int(baseline_key.split('_')[0])
            else:
                baseline_row = 0
        elif mode == "row":
            baseline_row = int(self.row_baseline_var.get()) if self.row_baseline_var.get() else 0
        else:
            baseline_row = 0
            
        for col in range(len(self.concurrent_sims)):
            self.dataset_selections[(baseline_row, col)].set(True)
        self.update_status()
    
    def update_status(self):
        """Update the status label"""
        selected_count = sum(1 for var in self.dataset_selections.values() if var.get())
        mode = self.baseline_mode.get()
        
        # Get baseline information based on current mode
        if mode == "single":
            baseline_key = self.single_baseline_var.get()
            if baseline_key and '_' in baseline_key:
                baseline_row, baseline_col = map(int, baseline_key.split('_'))
                baseline_threads = self.thread_counts[baseline_row]
                baseline_sims = self.concurrent_sims[baseline_col]
                baseline_info = f"{baseline_threads} threads, {baseline_sims} sims"
            else:
                baseline_info = "None selected"
        elif mode == "row":
            baseline_row = int(self.row_baseline_var.get()) if self.row_baseline_var.get() else 0
            baseline_threads = self.thread_counts[baseline_row]
            baseline_info = f"Row: {baseline_threads} threads"
        elif mode == "column":
            baseline_col = int(self.column_baseline_var.get()) if self.column_baseline_var.get() else 0
            baseline_sims = self.concurrent_sims[baseline_col]
            baseline_info = f"Column: {baseline_sims} sims"
        else:
            baseline_info = "Unknown mode"
        
        self.status_label.config(text=f"Selected: {selected_count} datasets | Baseline ({mode}): {baseline_info}")
    
    def get_mock_execution_time(self, threads, sims):
        """Generate mock execution time based on threading and simulation parameters"""
        # Base execution time for single thread, single sim
        base_time = 120.0
        
        # Threading efficiency factor (diminishing returns)
        thread_factor = 1.0 / max(1, threads ** 0.7)
        
        # Simulation concurrency penalty (resource contention)
        sim_penalty = 1.0 + (sims - 1) * 0.3
        
        # Memory/IO pressure for high concurrency
        if sims > 8:
            sim_penalty *= 1.5
        if sims > 32:
            sim_penalty *= 2.0
            
        return base_time * thread_factor * sim_penalty
    
    def on_single_baseline_change(self, row, col):
        """Handle single dataset baseline selection"""
        threads = self.thread_counts[row]
        sims = self.concurrent_sims[col]
        print(f"Single baseline changed to: {threads} threads, {sims} sims")
        self.update_status()
    
    def on_row_baseline_change(self, row):
        """Handle row baseline selection"""
        threads = self.thread_counts[row]
        print(f"Row baseline changed to: {threads} threads")
        self.update_status()
    
    def on_column_baseline_change(self, col):
        """Handle column baseline selection"""
        sims = self.concurrent_sims[col]
        print(f"Column baseline changed to: {sims} sims")
        self.update_status()
    
    def update_radio_visibility(self):
        """Update visibility of radio buttons based on baseline mode"""
        mode = self.baseline_mode.get()
        
        # Handle single baseline radio buttons (in individual cells)
        for rb in getattr(self, 'single_baseline_radios', []):
            if mode == "single":
                rb.pack(anchor=tk.CENTER)
            else:
                rb.pack_forget()
        
        # Handle row baseline radio buttons (in row headers) 
        for rb in getattr(self, 'row_baseline_radios', []):
            if mode == "row":
                rb.place(relx=0.75, rely=0.5, anchor=tk.CENTER)  # Position in corner of row header
            else:
                rb.place_forget()
        
        # Handle column baseline radio buttons (in column headers)
        for rb in getattr(self, 'column_baseline_radios', []):
            if mode == "column":
                rb.place(relx=0.8, rely=0.5, anchor=tk.CENTER)  # Position in corner of column header
            else:
                rb.place_forget()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Run the UI mockup"""
    print("EnergyPlus Concurrent Simulation Explorer - UI Mockup")
    print("This shows the proposed interface layout.")
    print("\nFeatures demonstrated:")
    print("- Chart area for overlaid performance comparisons")
    print("- 7x6 matrix for dataset selection (checkboxes)")
    print("- Radio buttons for baseline selection")
    print("- Control buttons for chart updates")
    print("\nPlease review the layout and provide feedback!")
    
    app = SimulationExplorerUI()
    app.run()


if __name__ == "__main__":
    main()