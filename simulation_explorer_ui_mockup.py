"""
EnergyPlus Concurrent Simulation Explorer - UI Design Mockup
This is a design prototype to establish the interface layout before full implementation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import os


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
        self.function_ordering = tk.StringVar(value="alphabetic")  # Function ordering: "alphabetic" or "magnitude"
        
        # Baseline selection variables for different modes
        self.single_baseline_var = tk.StringVar()  # For single dataset baseline
        self.row_baseline_var = tk.StringVar()     # For row baseline
        self.column_baseline_var = tk.StringVar()  # For column baseline
        
        # Data storage
        self.project_data = None  # Will store loaded project JSON
        self.simulation_data = {}  # Will store all loaded simulation data {(row,col): data}
        self.current_project_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the main UI layout with resizable panels"""
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Configure root window for resizing
        self.root.grid_rowconfigure(1, weight=1)  # Changed from 0 to 1 to account for toolbar
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main horizontal paned window for resizable panels
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
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
        
        # Auto-load project file if it exists in current directory
        self.auto_load_project_file()
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Project...", command=self.load_project_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export Chart...", command=self.export_chart, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Statistics Panel", variable=self.show_stats_panel, 
                                 command=self.toggle_stats_panel)
        view_menu.add_checkbutton(label="Show Function Labels", variable=self.show_function_labels,
                                 command=self.update_chart)
        view_menu.add_separator()
        
        # Function ordering submenu
        ordering_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Function Ordering", menu=ordering_menu)
        ordering_menu.add_radiobutton(label="Alphabetical", variable=self.function_ordering, 
                                     value="alphabetic", command=self.update_chart)
        ordering_menu.add_radiobutton(label="By Magnitude (Largest First)", variable=self.function_ordering,
                                     value="magnitude", command=self.update_chart)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Update Chart", command=self.update_chart, accelerator="F5")
        analysis_menu.add_command(label="Clear All Selections", command=self.clear_selections, accelerator="Ctrl+D")
        analysis_menu.add_separator()
        
        # Baseline mode submenu
        baseline_menu = tk.Menu(analysis_menu, tearoff=0)
        analysis_menu.add_cascade(label="Baseline Mode", menu=baseline_menu)
        baseline_menu.add_radiobutton(label="Single Dataset", variable=self.baseline_mode, 
                                     value="single", command=self.update_comparison_mode)
        baseline_menu.add_radiobutton(label="Row Comparison", variable=self.baseline_mode,
                                     value="row", command=self.update_comparison_mode)
        baseline_menu.add_radiobutton(label="Column Comparison", variable=self.baseline_mode,
                                     value="column", command=self.update_comparison_mode)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.load_project_file())
        self.root.bind('<Control-s>', lambda e: self.export_chart())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-d>', lambda e: self.clear_selections())
        self.root.bind('<F5>', lambda e: self.update_chart())
    
    def create_toolbar(self):
        """Create a toolbar with quick access buttons"""
        
        # Create toolbar frame
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 0))
        
        # Load project button (prominent)
        load_btn = ttk.Button(toolbar, text="📁 Load Project", 
                             command=self.load_project_file)
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Update chart button
        update_btn = ttk.Button(toolbar, text="📊 Update Chart", 
                               command=self.update_chart)
        update_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export chart button
        export_btn = ttk.Button(toolbar, text="💾 Export Chart", 
                               command=self.export_chart)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Clear selections button
        clear_btn = ttk.Button(toolbar, text="🗑️ Clear All", 
                              command=self.clear_selections)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick select buttons
        select_row_btn = ttk.Button(toolbar, text="→ Select Row", 
                                   command=self.select_current_row)
        select_row_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        select_col_btn = ttk.Button(toolbar, text="↓ Select Column", 
                                   command=self.select_current_column)
        select_col_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Baseline mode quick buttons
        ttk.Label(toolbar, text="Baseline:").pack(side=tk.LEFT, padx=(0, 5))
        
        single_btn = ttk.Radiobutton(toolbar, text="Single", 
                                    variable=self.baseline_mode, value="single",
                                    command=self.update_comparison_mode)
        single_btn.pack(side=tk.LEFT)
        
        row_btn = ttk.Radiobutton(toolbar, text="Row", 
                                 variable=self.baseline_mode, value="row",
                                 command=self.update_comparison_mode)
        row_btn.pack(side=tk.LEFT)
        
        col_btn = ttk.Radiobutton(toolbar, text="Column", 
                                 variable=self.baseline_mode, value="column",
                                 command=self.update_comparison_mode)
        col_btn.pack(side=tk.LEFT)
    
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
        """Create the dataset selection table with full scrollable content"""
        
        # Configure parent for expansion
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Main selection frame
        selection_frame = ttk.LabelFrame(parent, text="Dataset Selection Matrix", padding="5")
        selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        selection_frame.grid_rowconfigure(2, weight=1)
        selection_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions (fixed at top)
        instructions = ttk.Label(selection_frame, 
                               text="Select datasets to overlay (checkboxes) and baseline reference (radio button):")
        instructions.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Status and baseline controls container (same region)
        status_baseline_frame = ttk.Frame(selection_frame)
        status_baseline_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        status_baseline_frame.grid_columnconfigure(0, weight=1)
        
        # Status label (left side of the container)
        self.status_label = ttk.Label(status_baseline_frame, text="Ready - Load project data to begin")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Baseline comparison mode (right side of the same container) - inline for shortest profile
        baseline_frame = ttk.Frame(status_baseline_frame)
        baseline_frame.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        ttk.Label(baseline_frame, text="Baseline:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(baseline_frame, text="Single", variable=self.baseline_mode, value="single",
                       command=self.update_comparison_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(baseline_frame, text="Row", variable=self.baseline_mode, value="row",
                       command=self.update_comparison_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(baseline_frame, text="Column", variable=self.baseline_mode, value="column",
                       command=self.update_comparison_mode).pack(side=tk.LEFT)
        
        # Create scrollable container for all content
        self.create_scrollable_content(selection_frame)
    
    def create_scrollable_content(self, parent):
        """Create a fully scrollable area for table and controls"""
        
        # Create main scrollable container
        scroll_container = ttk.Frame(parent)
        scroll_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)
        
        # Create canvas for scrolling
        self.content_canvas = tk.Canvas(scroll_container, highlightthickness=0)
        
        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=self.content_canvas.yview)
        
        # Create horizontal scrollbar  
        h_scrollbar = ttk.Scrollbar(scroll_container, orient=tk.HORIZONTAL, command=self.content_canvas.xview)
        
        # Configure canvas scrolling
        self.content_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Create scrollable frame inside canvas
        self.scrollable_frame = ttk.Frame(self.content_canvas)
        
        # Bind frame resize to update scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        )
        
        # Create window in canvas for the scrollable frame
        self.canvas_window = self.content_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        
        # Grid the canvas and scrollbars
        self.content_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Enable mouse wheel scrolling
        self.bind_mousewheel(self.content_canvas)
        
        # Create all content in the scrollable frame
        self.create_all_table_content(self.scrollable_frame)
    
    def bind_mousewheel(self, canvas):
        """Bind mouse wheel events for scrolling"""
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mousewheel events to canvas and its children
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Shift-MouseWheel>", on_shift_mousewheel)
    
    def create_all_table_content(self, parent):
        """Create table and controls in the scrollable area"""
        
        # Create table header
        self.create_table_header(parent)
        
        # Create table rows
        self.create_table_rows(parent)
        
        # Add some spacing
        spacer = ttk.Frame(parent, height=20)
        spacer.grid(row=10, column=0, columnspan=25, pady=10)
        
        # Create control buttons in scrollable area
        self.create_control_buttons(parent)
    
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
                exec_time = self.get_real_execution_time(row_idx, sim_idx)
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
        
        # Load project data button (prominent)
        load_btn = ttk.Button(button_frame, text="Load Project Data", 
                             command=self.load_project_file)
        load_btn.pack(side=tk.LEFT, padx=(0, 15))
        
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
    
    def sort_functions_by_preference(self, function_names, selected_datasets, baseline_functions):
        """Sort functions based on user preference: alphabetic or by magnitude"""
        
        ordering = self.function_ordering.get()
        
        if ordering == "alphabetic":
            # Simple alphabetical sorting
            return sorted(function_names)
        
        elif ordering == "magnitude":
            # Sort by maximum performance ratio across all selected datasets
            function_max_ratios = {}
            
            for func_name in function_names:
                max_ratio = 0.0
                baseline_time = baseline_functions.get(func_name, {}).get('total_time', 1.0)
                
                if baseline_time > 0:
                    # Calculate max ratio across all selected datasets for this function
                    for dataset in selected_datasets:
                        dataset_functions = dataset['data'].get('functions', {})
                        if func_name in dataset_functions:
                            dataset_time = dataset_functions[func_name]['total_time']
                            ratio = dataset_time / baseline_time
                            max_ratio = max(max_ratio, ratio)
                
                function_max_ratios[func_name] = max_ratio
            
            # Sort by maximum ratio (descending - largest first)
            return sorted(function_names, key=lambda f: function_max_ratios.get(f, 0), reverse=True)
        
        else:
            # Default fallback to alphabetical
            return sorted(function_names)
    
    def create_demo_chart(self):
        """Create a chart with real or demo data based on what's loaded"""
        
        if self.simulation_data:
            self.create_real_data_chart()
        else:
            self.create_mock_data_chart()
    
    def create_real_data_chart(self):
        """Create chart using real loaded simulation data"""
        
        print("Creating chart with real data...")
        
        # Get selected datasets
        selected_datasets = []
        baseline_data = None
        
        for (row_idx, col_idx), var in self.dataset_selections.items():
            if var.get() and (row_idx, col_idx) in self.simulation_data:
                data = self.simulation_data[(row_idx, col_idx)]
                threads = self.thread_counts[row_idx]
                sims = self.concurrent_sims[col_idx]
                selected_datasets.append({
                    'name': f"{sims} sim{'s' if sims > 1 else ''}, {threads} thread{'s' if threads > 1 else ''}",
                    'data': data,
                    'threads': threads,
                    'sims': sims,
                    'coords': (row_idx, col_idx)
                })
                print(f"Added dataset: {sims} sims, {threads} threads")
        
        if not selected_datasets:
            self.ax.clear()
            data_count = len(self.simulation_data)
            selected_count = sum(1 for var in self.dataset_selections.values() if var.get())
            self.ax.text(0.5, 0.5, 
                        f'No valid datasets selected.\n\nLoaded: {data_count} datasets\nSelected: {selected_count} datasets\n\nSelect datasets with loaded data to visualize.',
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        print(f"Found {len(selected_datasets)} selected datasets with real data")
        
        # Get baseline data based on current mode
        baseline_data = self.get_baseline_data()
        
        if not baseline_data:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'Baseline data not available.\nPlease select a valid baseline with loaded data.',
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        # Extract function names from the baseline dataset
        baseline_functions = baseline_data.get('functions', {})
        if not baseline_functions:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No function data available in baseline dataset.',
                        ha='center', va='center', transform=self.ax.transAxes, fontsize=12)
            self.canvas.draw()
            return
        
        function_names = list(baseline_functions.keys())
        print(f"Found {len(function_names)} functions in baseline data")
        
        # Sort functions based on user preference
        function_names = self.sort_functions_by_preference(function_names, selected_datasets, baseline_functions)
        print(f"Functions sorted by {self.function_ordering.get()} order")
        
        self.ax.clear()
        
        # Create performance ratios for each dataset
        bar_width = 0.8
        x = np.arange(len(function_names))
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        for i, dataset in enumerate(selected_datasets):
            ratios = []
            dataset_functions = dataset['data'].get('functions', {})
            
            for func_name in function_names:
                baseline_time = baseline_functions[func_name]['total_time']
                if func_name in dataset_functions and baseline_time > 0:
                    dataset_time = dataset_functions[func_name]['total_time']
                    ratio = dataset_time / baseline_time
                else:
                    ratio = 1.0  # Default if function missing
                ratios.append(ratio)
            
            print(f"Dataset {dataset['name']}: ratios range {min(ratios):.2f} - {max(ratios):.2f}")
            
            # Plot bars for this dataset
            self.ax.bar(x, ratios, bar_width, 
                       alpha=0.7, 
                       color=colors[i % len(colors)],
                       label=dataset['name'])
        
        # Add baseline reference line
        self.ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.8, linewidth=2, label='Baseline')
        
        # Formatting
        self.ax.set_ylabel('Performance Ratio (Normalized to Baseline)')
        self.ax.set_title('EnergyPlus Function Performance Comparison')
        self.ax.set_xticks(x)
        
        # Toggle function labels based on user preference
        if self.show_function_labels.get():
            # Abbreviate long function names for better display
            abbreviated_names = [self.abbreviate_function_name(name) for name in function_names]
            self.ax.set_xticklabels(abbreviated_names, rotation=45, ha='right')
            self.ax.set_xlabel('Functions')
            # Adjust margins for rotated labels
            self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.25)
        else:
            self.ax.set_xticklabels([''] * len(function_names))
            self.ax.set_xlabel('')
            self.figure.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.05)
        
        # Add legend
        self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        self.ax.grid(True, alpha=0.3)
        
        # Store function names for hover functionality
        self.function_names = function_names
        self.dataset_names = [d['name'] for d in selected_datasets]
        
        self.canvas.draw()
        
        # Restore function highlighting after chart redraw
        if self.selected_functions:
            self.highlight_selected_functions()
    
    def create_mock_data_chart(self):
        """Create demo chart when no real data is loaded"""
        
        # Demo data for visualization concept
        functions = ['Function A', 'Function B', 'Function C', 'Function D', 'Function E']
        
        # Simulate different performance ratios for overlaid datasets
        datasets = [
            {'name': '1 sim, 1 thread', 'ratios': [1.0, 1.0, 1.0, 1.0, 1.0], 'alpha': 0.7},
            {'name': '2 sims, 2 threads', 'ratios': [1.2, 0.8, 1.1, 0.9, 1.3], 'alpha': 0.7},
            {'name': '4 sims, 4 threads', 'ratios': [1.8, 0.6, 1.5, 0.7, 2.1], 'alpha': 0.7},
        ]
        
        # Apply sorting to demo functions
        if self.function_ordering.get() == "magnitude":
            # Sort by maximum ratio across all datasets (descending)
            max_ratios = {}
            for i, func in enumerate(functions):
                max_ratio = max(dataset['ratios'][i] for dataset in datasets)
                max_ratios[func] = max_ratio
            
            # Create sorted order and reorder all data accordingly
            sorted_indices = sorted(range(len(functions)), 
                                  key=lambda i: max_ratios[functions[i]], reverse=True)
            functions = [functions[i] for i in sorted_indices]
            for dataset in datasets:
                dataset['ratios'] = [dataset['ratios'][i] for i in sorted_indices]
        else:
            # Alphabetical sorting (default)
            sorted_indices = sorted(range(len(functions)), key=lambda i: functions[i])
            functions = [functions[i] for i in sorted_indices]
            for dataset in datasets:
                dataset['ratios'] = [dataset['ratios'][i] for i in sorted_indices]
        
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
        self.ax.set_title('Overlaid Performance Comparison - Demo Chart (Load data for real analysis)')
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
        
        # Restore function highlighting after chart redraw
        if self.selected_functions:
            self.highlight_selected_functions()
    
    def get_baseline_data(self):
        """Get baseline data based on current baseline mode"""
        
        mode = self.baseline_mode.get()
        print(f"Getting baseline data for mode: {mode}")
        
        if mode == "single":
            baseline_key = self.single_baseline_var.get()
            if baseline_key and '_' in baseline_key:
                baseline_row, baseline_col = map(int, baseline_key.split('_'))
                baseline_data = self.simulation_data.get((baseline_row, baseline_col))
                if baseline_data:
                    threads = self.thread_counts[baseline_row]
                    sims = self.concurrent_sims[baseline_col]
                    print(f"Using single baseline: {threads} threads, {sims} sims")
                    return baseline_data
                else:
                    print(f"Single baseline data not found for coordinates ({baseline_row}, {baseline_col})")
        elif mode == "row":
            baseline_row = int(self.row_baseline_var.get()) if self.row_baseline_var.get() else 0
            # Use first available column as baseline for row comparison
            for col in range(len(self.concurrent_sims)):
                if (baseline_row, col) in self.simulation_data:
                    baseline_data = self.simulation_data.get((baseline_row, col))
                    threads = self.thread_counts[baseline_row]
                    sims = self.concurrent_sims[col]
                    print(f"Using row baseline: {threads} threads, {sims} sims")
                    return baseline_data
            print(f"No row baseline data found for row {baseline_row}")
        elif mode == "column":
            baseline_col = int(self.column_baseline_var.get()) if self.column_baseline_var.get() else 0
            # Use first available row as baseline for column comparison
            for row in range(len(self.thread_counts)):
                if (row, baseline_col) in self.simulation_data:
                    baseline_data = self.simulation_data.get((row, baseline_col))
                    threads = self.thread_counts[row]
                    sims = self.concurrent_sims[baseline_col]
                    print(f"Using column baseline: {threads} threads, {sims} sims")
                    return baseline_data
            print(f"No column baseline data found for column {baseline_col}")
        
        # Fallback: try to get any available data as baseline
        if self.simulation_data:
            fallback_key = list(self.simulation_data.keys())[0]
            fallback_data = self.simulation_data[fallback_key]
            threads = self.thread_counts[fallback_key[0]]
            sims = self.concurrent_sims[fallback_key[1]]
            print(f"Using fallback baseline: {threads} threads, {sims} sims")
            return fallback_data
        
        print("No baseline data available at all")
        return None
    
    def abbreviate_function_name(self, name):
        """Abbreviate long function names for better chart display"""
        if len(name) <= 20:
            return name
        
        # Common abbreviations for EnergyPlus functions
        abbreviations = {
            'SimulateHVAC': 'HVAC',
            'CalcAirLoopSplitter': 'AirSplit',
            'SimulateAirLoopComponents': 'AirComp',
            'UpdateZoneInletConvergenceLog': 'ZoneConv',
            'CalcMundtModel': 'Mundt',
            'SimulateWaterCoilComponents': 'WaterCoil',
            'GetZoneAirDistribution': 'ZoneAir',
            'SimulateAirZonePlenum': 'Plenum',
            'CalcHeatBalanceInsideSurf': 'HeatBalIn',
            'CalcUserDefinedInsideHVACPlant': 'UserHVAC',
            'ReportAirHeatBalance': 'AirHeatRpt',
            'ReportZoneMeanAirTemp': 'ZoneTempRpt',
            'ManageSystemAvailability': 'SysAvail',
            'InitLoadDistribution': 'LoadInit',
            'CalcWindowScreenThermal': 'WinScreen',
            'CalcAirSystem': 'AirSys',
            'CalcComplexWindowThermal': 'ComplexWin',
            'ReportSysSizing': 'SysSizeRpt',
            'CalcHeatBalanceOutsideSurf': 'HeatBalOut'
        }
        
        return abbreviations.get(name, name[:15] + '...')
    
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
        
        # Detect which function bar was clicked based on chart data
        if event.xdata is not None and hasattr(self, 'function_names'):
            func_index = int(round(event.xdata))
            if 0 <= func_index < len(self.function_names):
                func_name = self.function_names[func_index]
                
                if func_name in self.selected_functions:
                    self.selected_functions.remove(func_name)
                    print(f"Deselected function: {func_name}")
                else:
                    self.selected_functions.add(func_name)
                    print(f"Selected function: {func_name}")
                
                self.update_statistics()
                self.highlight_selected_functions()
        elif event.xdata is not None:
            # Fallback for demo data when no real function names available
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
        print("Chart update requested - checking data availability...")
        if self.simulation_data:
            print(f"Using real data ({len(self.simulation_data)} datasets loaded)")
            self.create_demo_chart()  # This method already handles real vs mock data
        else:
            print("No real data available - using mock data")
            self.create_demo_chart()
        print("Chart update completed")
    
    def clear_selections(self):
        """Clear all dataset selections"""
        for var in self.dataset_selections.values():
            var.set(False)
        self.update_status()
        self.update_statistics()
    
    def highlight_selected_functions(self):
        """Visual feedback for selected functions by highlighting bars"""
        selected_list = list(self.selected_functions)
        print(f"Currently selected functions: {selected_list}")
        
        # Clear any existing highlights and add new ones
        if hasattr(self, 'function_names') and hasattr(self, 'ax'):
            # Initialize highlight patches list if it doesn't exist
            if not hasattr(self, 'highlight_patches'):
                self.highlight_patches = []
            else:
                # Only try to remove patches if the axes hasn't been cleared
                # (chart redraw clears all patches automatically)
                try:
                    for patch in self.highlight_patches:
                        if patch in self.ax.patches:
                            patch.remove()
                except (NotImplementedError, ValueError, AttributeError):
                    # If removal fails, patches were likely already cleared by chart redraw
                    pass
            
            self.highlight_patches = []
            
            # Add highlight rectangles for selected functions
            for func_name in self.selected_functions:
                if func_name in self.function_names:
                    func_index = self.function_names.index(func_name)
                    
                    # Get the current y-axis limits to size the highlight rectangle
                    y_min, y_max = self.ax.get_ylim()  
                    
                    # Create a semi-transparent rectangle to highlight the selected function
                    highlight = plt.Rectangle(
                        (func_index - 0.4, y_min), 0.8, y_max - y_min,
                        alpha=0.2, color='yellow', zorder=0
                    )
                    self.ax.add_patch(highlight)
                    self.highlight_patches.append(highlight)
            
            # Redraw the canvas to show highlights
            self.canvas.draw_idle()
    
    def update_statistics(self):
        """Update the statistics panel based on selections"""
        self.stats_text.delete(1.0, tk.END)
        
        selected_datasets = sum(1 for var in self.dataset_selections.values() if var.get())
        baseline_mode = self.baseline_mode.get()
        
        # Check if we have real data
        using_real_data = bool(self.simulation_data)
        
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
        
        if using_real_data:
            project_name = self.project_data.get('project_info', {}).get('name', 'Unknown Project') if self.project_data else 'Unknown'
            stats_text += f"Project: {project_name}\n"
            stats_text += f"Loaded Datasets: {len(self.simulation_data)} of 42\n"
        else:
            stats_text += "Data Source: Mock/Demo Data\n"
            stats_text += "(Load real project data for actual analysis)\n"
        
        stats_text += f"Selected Datasets: {selected_datasets}\n"
        stats_text += f"Baseline: {baseline_threads} threads, {baseline_sims} sims\n"
        stats_text += f"Comparison Mode: {baseline_mode.capitalize()}\n"
        
        # Show details of selected datasets
        if selected_datasets > 0:
            stats_text += f"\nSELECTED DATASET DETAILS\n{'-'*25}\n"
            selected_coords = [(row, col) for (row, col), var in self.dataset_selections.items() if var.get()]
            for row, col in selected_coords:
                threads = self.thread_counts[row]
                sims = self.concurrent_sims[col]
                has_data = (row, col) in self.simulation_data
                status = "✓ Loaded" if has_data else "⚠ Not loaded"
                stats_text += f"• {sims} sim{'s' if sims > 1 else ''}, {threads} thread{'s' if threads > 1 else ''} - {status}\n"
                
                # If we have real data for this dataset, show performance metrics
                if has_data and using_real_data:
                    data = self.simulation_data[(row, col)]
                    metadata = data.get('metadata', {})
                    total_time = metadata.get('total_simulation_time', 0)
                    if total_time > 0:
                        stats_text += f"  Time: {total_time:.1f}s\n"
            stats_text += "\n"
        
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
            stats_text += f"SELECTED FUNCTIONS ({len(self.selected_functions)})\n{'-'*25}\n"
            
            # Show function-specific analysis if we have real data
            if using_real_data and selected_datasets > 0:
                baseline_data = self.get_baseline_data()
                if baseline_data and baseline_data.get('functions'):
                    baseline_functions = baseline_data.get('functions', {})
                    selected_coords = [(row, col) for (row, col), var in self.dataset_selections.items() if var.get()]
                    available_data = [(row, col) for row, col in selected_coords if (row, col) in self.simulation_data]
                    
                    for func in sorted(self.selected_functions):
                        if func in baseline_functions:
                            baseline_time = baseline_functions[func]['total_time']
                            stats_text += f"• {func}:\n"
                            stats_text += f"  Baseline: {baseline_time:.3f}s\n"
                            
                            # Collect performance across selected datasets
                            ratios = []
                            for row, col in available_data:
                                data = self.simulation_data[(row, col)]
                                functions = data.get('functions', {})
                                if func in functions and baseline_time > 0:
                                    func_time = functions[func]['total_time']
                                    ratio = func_time / baseline_time
                                    ratios.append(ratio)
                                    threads = self.thread_counts[row]
                                    sims = self.concurrent_sims[col]
                                    stats_text += f"  {sims}s,{threads}t: {ratio:.2f}x ({func_time:.3f}s)\n"
                            
                            if ratios:
                                min_ratio = min(ratios)
                                max_ratio = max(ratios)
                                avg_ratio = sum(ratios) / len(ratios)
                                stats_text += f"  Range: {min_ratio:.2f}x - {max_ratio:.2f}x (avg: {avg_ratio:.2f}x)\n"
                        else:
                            stats_text += f"• {func}: No data in baseline\n"
                        stats_text += "\n"
                else:
                    # Fallback for selected functions without baseline data
                    for func in sorted(self.selected_functions):
                        stats_text += f"• {func}\n"
                    stats_text += "\n"
            else:
                # Show basic function list for demo data or when no datasets selected
                for func in sorted(self.selected_functions):
                    stats_text += f"• {func}\n"
                stats_text += "\n"
        
        if using_real_data and selected_datasets > 0:
            # Analyze real data
            selected_coords = [(row, col) for (row, col), var in self.dataset_selections.items() if var.get()]
            available_data = [(row, col) for row, col in selected_coords if (row, col) in self.simulation_data]
            
            if available_data:
                stats_text += self.analyze_real_data(available_data, baseline_mode)
            else:
                stats_text += "No data available for selected datasets.\n"
                stats_text += "Selected datasets may not be loaded yet.\n"
        
        elif selected_datasets == 1:
            stats_text += "SINGLE DATASET ANALYSIS\n"
            stats_text += "-" * 25 + "\n"
            if using_real_data:
                stats_text += "Real dataset analysis will appear here\n"
                stats_text += "when single dataset is selected.\n"
            else:
                stats_text += "Dataset Context (Mock Data):\n"
                stats_text += "• Total simulation time: 156.1s\n"
                stats_text += "• Performance ratio: 0.40x\n"
                stats_text += "• Memory usage: 2.1 GB\n"
                stats_text += "• CPU utilization: 95%\n"
                stats_text += "• Resource contention: Low\n\n"
            
            if self.selected_functions:
                stats_text += "Function-Specific Metrics:\n"
                for func in sorted(self.selected_functions):
                    stats_text += f"• {func}: 1.2x baseline (estimated)\n"
            
        elif selected_datasets > 1:
            stats_text += "MULTI-DATASET COMPARISON\n"
            stats_text += "-" * 27 + "\n"
            if using_real_data:
                stats_text += "Multi-dataset analysis will appear here\n"
                stats_text += "when multiple datasets are selected.\n"
            else:
                stats_text += "Performance Statistics (Mock Data):\n"
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
                    stats_text += f"• {func}: 0.6x - 2.8x range (estimated)\n"
        
        else:
            stats_text += "No datasets selected.\n"
            stats_text += "Select datasets from the matrix below to see analysis."
        
        self.stats_text.insert(1.0, stats_text)
    
    def analyze_real_data(self, selected_coords, baseline_mode):
        """Analyze real data for selected coordinates"""
        
        analysis = "REAL DATA ANALYSIS\n" + "-" * 20 + "\n"
        
        # Get baseline data for comparison
        baseline_data = self.get_baseline_data()
        if not baseline_data:
            return analysis + "Baseline data not available for comparison.\n"
        
        # Collect performance data
        performance_times = []
        memory_usages = []
        cpu_utilizations = []
        
        for row, col in selected_coords:
            if (row, col) in self.simulation_data:
                data = self.simulation_data[(row, col)]
                metadata = data.get('metadata', {})
                
                # Collect metrics
                total_time = metadata.get('total_simulation_time', 0)
                memory_gb = metadata.get('system_conditions', {}).get('estimated_memory_usage_gb', 0)
                cpu_percent = metadata.get('system_conditions', {}).get('cpu_utilization_percent', 0)
                
                performance_times.append(total_time)
                memory_usages.append(memory_gb)
                cpu_utilizations.append(cpu_percent)
        
        if performance_times:
            # Calculate statistics
            min_time = min(performance_times)
            max_time = max(performance_times)
            avg_time = sum(performance_times) / len(performance_times)
            
            baseline_time = baseline_data.get('metadata', {}).get('total_simulation_time', 1)
            min_ratio = min_time / baseline_time if baseline_time > 0 else 0
            max_ratio = max_time / baseline_time if baseline_time > 0 else 0
            avg_ratio = avg_time / baseline_time if baseline_time > 0 else 0
            
            analysis += f"Performance Overview:\n"
            analysis += f"• Datasets analyzed: {len(selected_coords)}\n"
            analysis += f"• Best performance: {min_time:.1f}s ({min_ratio:.2f}x baseline)\n"
            analysis += f"• Worst performance: {max_time:.1f}s ({max_ratio:.2f}x baseline)\n"
            analysis += f"• Average performance: {avg_time:.1f}s ({avg_ratio:.2f}x baseline)\n\n"
            
            if memory_usages:
                analysis += f"System Resource Usage:\n"
                analysis += f"• Memory range: {min(memory_usages):.1f} - {max(memory_usages):.1f} GB\n"
                analysis += f"• CPU utilization: {min(cpu_utilizations)} - {max(cpu_utilizations)}%\n\n"
            
            # Function-level analysis if functions are selected
            if self.selected_functions and baseline_data.get('functions'):
                analysis += "Selected Function Performance:\n"
                baseline_functions = baseline_data.get('functions', {})
                
                for func in sorted(self.selected_functions):
                    if func in baseline_functions:
                        baseline_func_time = baseline_functions[func]['total_time']
                        func_ratios = []
                        
                        for row, col in selected_coords:
                            if (row, col) in self.simulation_data:
                                data = self.simulation_data[(row, col)]
                                functions = data.get('functions', {})
                                if func in functions and baseline_func_time > 0:
                                    func_time = functions[func]['total_time']
                                    ratio = func_time / baseline_func_time
                                    func_ratios.append(ratio)
                        
                        if func_ratios:
                            min_func_ratio = min(func_ratios)
                            max_func_ratio = max(func_ratios)
                            analysis += f"• {func}: {min_func_ratio:.2f}x - {max_func_ratio:.2f}x\n"
        
        return analysis
    
    def export_chart(self):
        """Export the current chart as an image file"""
        
        if not hasattr(self, 'figure'):
            messagebox.showwarning("Warning", "No chart available to export.")
            return
        
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            title="Export Chart",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"), 
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.figure.savefig(filename, dpi=300, bbox_inches='tight', 
                                   facecolor='white', edgecolor='none')
                messagebox.showinfo("Success", f"Chart exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export chart:\n{e}")
    
    def show_about(self):
        """Show about dialog"""
        
        about_text = """EnergyPlus Concurrent Simulation Explorer

A GUI application for analyzing and visualizing EnergyPlus simulation 
performance data across different threading and concurrency configurations.

Features:
• Load project files with multiple datasets
• Interactive performance comparison charts  
• Real-time statistical analysis
• Flexible baseline comparison modes
• Function-level performance tracking

Version: 1.0
Built with: Python, tkinter, matplotlib

Use Ctrl+O to load project data and get started!"""
        
        messagebox.showinfo("About EnergyPlus Explorer", about_text)
    
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
    
    def auto_load_project_file(self):
        """Automatically load project file if it exists in current directory"""
        
        # Look for the standard project file name
        project_files = ['energyplus_project.json', 'project.json', 'data.json']
        
        for filename in project_files:
            if os.path.exists(filename):
                try:
                    # Load project JSON
                    with open(filename, 'r') as f:
                        self.project_data = json.load(f)
                    
                    self.current_project_path = os.path.abspath(filename)
                    project_dir = os.path.dirname(self.current_project_path)
                    
                    # Validate project structure
                    if 'datasets' not in self.project_data:
                        continue  # Try next file
                    
                    # Load all simulation data files
                    self.simulation_data = {}
                    
                    for sim_count, thread_data in self.project_data['datasets'].items():
                        for thread_count, data_filename in thread_data.items():
                            # Construct full path
                            file_path = os.path.join(project_dir, data_filename)
                            
                            if os.path.exists(file_path):
                                try:
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                    
                                    # Map to matrix coordinates
                                    sim_idx = self.get_sim_index(sim_count)
                                    thread_idx = self.get_thread_index(thread_count)
                                    
                                    if sim_idx is not None and thread_idx is not None:
                                        self.simulation_data[(thread_idx, sim_idx)] = data
                                
                                except json.JSONDecodeError:
                                    continue  # Skip invalid files
                    
                    # Update the UI with real data if we loaded some
                    if self.simulation_data:
                        self.update_table_with_real_data()
                        self.update_status()
                        
                        # Update status to show auto-loaded data
                        project_name = self.project_data.get('project_info', {}).get('name', filename)
                        loaded_count = len(self.simulation_data)
                        print(f"Auto-loaded project: {project_name} ({loaded_count} datasets)")
                        return  # Successfully loaded, stop trying other files
                
                except Exception as e:
                    print(f"Failed to auto-load {filename}: {e}")
                    continue  # Try next file
    
    def load_project_file(self):
        """Load a project JSON file that references all simulation data files"""
        
        # Ask user to select project file
        project_path = filedialog.askopenfilename(
            title="Select EnergyPlus Project File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if not project_path:
            return
        
        try:
            # Load project JSON
            with open(project_path, 'r') as f:
                self.project_data = json.load(f)
            
            self.current_project_path = project_path
            project_dir = os.path.dirname(project_path)
            
            # Validate project structure
            if 'datasets' not in self.project_data:
                messagebox.showerror("Error", "Invalid project file: missing 'datasets' section")
                return
            
            # Load all simulation data files
            self.simulation_data = {}
            missing_files = []
            
            for sim_count, thread_data in self.project_data['datasets'].items():
                for thread_count, filename in thread_data.items():
                    # Construct full path
                    file_path = os.path.join(project_dir, filename)
                    
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                            
                            # Map to matrix coordinates
                            sim_idx = self.get_sim_index(sim_count)
                            thread_idx = self.get_thread_index(thread_count)
                            
                            if sim_idx is not None and thread_idx is not None:
                                self.simulation_data[(thread_idx, sim_idx)] = data
                        
                        except json.JSONDecodeError as e:
                            messagebox.showerror("Error", f"Invalid JSON in {filename}: {e}")
                            return
                    else:
                        missing_files.append(filename)
            
            if missing_files:
                messagebox.showwarning("Warning", 
                    f"Some data files not found:\n" + "\n".join(missing_files[:10]) + 
                    (f"\n... and {len(missing_files) - 10} more" if len(missing_files) > 10 else ""))
            
            # Update the UI with real data
            self.update_table_with_real_data()
            self.update_status()
            
            # Show success message
            project_name = self.project_data.get('project_info', {}).get('name', 'Unknown Project')
            loaded_count = len(self.simulation_data)
            messagebox.showinfo("Success", 
                f"Loaded project: {project_name}\n{loaded_count} datasets loaded successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load project file: {e}")
    
    def get_sim_index(self, sim_key):
        """Convert sim key from project file to index in concurrent_sims array"""
        sim_map = {
            "1_sim": 0, "2_sims": 1, "4_sims": 2, "8_sims": 3, 
            "16_sims": 4, "32_sims": 5, "64_sims": 6
        }
        return sim_map.get(sim_key)
    
    def get_thread_index(self, thread_key):
        """Convert thread key from project file to index in thread_counts array"""
        thread_map = {
            "1_thread": 0, "2_threads": 1, "4_threads": 2, 
            "8_threads": 3, "16_threads": 4, "32_threads": 5
        }
        return thread_map.get(thread_key)
    
    def update_table_with_real_data(self):
        """Update the table display with real execution times from loaded data"""
        
        if not self.simulation_data:
            return
        
        print(f"Updating table with real data for {len(self.simulation_data)} datasets...")
        
        # Update time labels in the table
        for (thread_idx, sim_idx), data in self.simulation_data.items():
            if hasattr(self, 'table_frame'):
                # Find the time label for this position
                table_row = thread_idx + 2  # Account for header rows
                start_col = 1 + (sim_idx * 3)  # Time column
                
                # Get real execution time from data
                total_time = data.get('metadata', {}).get('total_simulation_time', 0)
                
                # Find and update the time label
                updated = False
                for widget in self.table_frame.grid_slaves():
                    info = widget.grid_info()
                    if info['row'] == table_row and info['column'] == start_col:
                        if isinstance(widget, ttk.Label):
                            # Update with real time and visual indicator
                            widget.config(text=f"{total_time:.1f}s", foreground='lime', background='darkgreen')
                            updated = True
                            break
                
                if updated:
                    print(f"Updated cell ({thread_idx}, {sim_idx}) with real time: {total_time:.1f}s")
        
        # Force a chart update to use real data
        self.update_chart()
        
        # Auto-select some interesting datasets for immediate visualization
        self.auto_select_datasets()
        
        print("Table update complete - real execution times now displayed")
    
    def auto_select_datasets(self):
        """Automatically select some interesting datasets when real data is loaded"""
        
        if not self.simulation_data:
            return
        
        # Clear current selections
        for var in self.dataset_selections.values():
            var.set(False)
        
        # Select some interesting combinations that are likely to be loaded
        interesting_combinations = [
            (0, 0),  # 1 thread, 1 sim - baseline
            (1, 1),  # 2 threads, 2 sims
            (3, 2),  # 8 threads, 4 sims
            (4, 3),  # 16 threads, 8 sims
            (0, 3),  # 1 thread, 8 sims - high contention
        ]
        
        selected_count = 0
        for thread_idx, sim_idx in interesting_combinations:
            if (thread_idx, sim_idx) in self.simulation_data:
                self.dataset_selections[(thread_idx, sim_idx)].set(True)
                selected_count += 1
                threads = self.thread_counts[thread_idx]
                sims = self.concurrent_sims[sim_idx]
                print(f"Auto-selected: {threads} threads, {sims} sims")
        
        if selected_count > 0:
            # Set baseline to first available dataset (1 thread, 1 sim if available)
            if (0, 0) in self.simulation_data:
                self.single_baseline_var.set("0_0")
            
            print(f"Auto-selected {selected_count} datasets for immediate visualization")
            self.update_status()
            self.update_chart()
    
    def get_real_execution_time(self, thread_idx, sim_idx):
        """Get real execution time from loaded data, fallback to mock if not available"""
        
        if (thread_idx, sim_idx) in self.simulation_data:
            return self.simulation_data[(thread_idx, sim_idx)].get('metadata', {}).get('total_simulation_time', 0)
        else:
            # Fallback to mock data
            threads = self.thread_counts[thread_idx]
            sims = self.concurrent_sims[sim_idx]
            return self.get_mock_execution_time(threads, sims)
    
    def on_selection_change(self, row, col):
        """Handle checkbox selection changes"""
        self.update_status()
        print(f"Selection changed: {self.concurrent_sims[row]} sims, {self.thread_counts[col]} threads")
    
    def on_baseline_change(self, row):
        """Handle baseline selection changes"""
        self.baseline_selection = (row, 0)  # For now, assume first thread count
        self.update_status()
        print(f"Baseline changed to: {self.concurrent_sims[row]} sims")
    
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
        
        # Check if real data is loaded
        data_status = f"Real data: {len(self.simulation_data)} datasets" if self.simulation_data else "Mock data"
        
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
        
        self.status_label.config(text=f"{data_status} | Selected: {selected_count} | Baseline ({mode}): {baseline_info}")
    
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
    """Run the EnergyPlus Concurrent Simulation Explorer"""
    print("EnergyPlus Concurrent Simulation Explorer - Performance Analysis Tool")
    print("Features:")
    print("• Interactive chart area for overlaid performance comparisons")
    print("• 7×6 matrix for dataset selection (thread counts vs concurrent simulations)")
    print("• Flexible baseline comparison modes (Single/Row/Column)")
    print("• Real-time statistical analysis panel")
    print("• Project file loading with auto-detection")
    print("• Menu bar and toolbar for easy access")
    print("• Chart export capabilities")
    print("• Keyboard shortcuts (Ctrl+O, F5, etc.)")
    print()
    print("Use 'Load Project Data' or Ctrl+O to get started!")
    print("Project file will auto-load if 'energyplus_project.json' exists in current directory.")
    print()
    
    app = SimulationExplorerUI()
    app.run()


if __name__ == "__main__":
    main()