# EnergyPlus Concurrent Simulation Explorer

A GUI application for analyzing and visualizing EnergyPlus simulation performance data across different threading and concurrency configurations.

## Features

## Real Data Visualization Features

### ✅ **Complete Dataset Integration**
- **42 Simulation Datasets**: Full matrix of thread counts (1-32) × concurrent simulations (1-64)
- **48 Functions per Dataset**: Comprehensive EnergyPlus function performance tracking
- **Realistic Performance Data**: Actual simulation times ranging from 156s to 81,819s
- **Auto-Loading**: Automatic detection and loading of project data on startup

### ✅ **Data Selection Matrix**
- **Real Execution Times**: Matrix displays actual simulation times from loaded data
- **Visual Indicators**: Real data shown with lime text on dark green background
- **Auto-Selection**: Intelligent selection of interesting datasets for immediate analysis
- **Interactive Selection**: Click checkboxes to select/deselect specific configurations

### ✅ **Performance Analysis Charts**
- **Real Function Data**: Charts display actual function performance ratios
- **Baseline Comparison**: Compare against real baseline performance data
- **Multiple Datasets**: Overlay multiple real simulation results
- **Function Abbreviation**: Smart abbreviation of long EnergyPlus function names

### User Interface
- **Menu Bar**: Full menu system with File, View, Analysis, and Help menus
- **Toolbar**: Quick access buttons with icons for common operations
- **Keyboard Shortcuts**: 
  - Ctrl+O: Load project file
  - Ctrl+S: Export chart
  - F5: Update chart
  - Ctrl+D: Clear all selections
  - Ctrl+Q: Exit application
- **Resizable Panels**: Adjustable chart and data selection areas
- **Scrollable Content**: Full access to all datasets regardless of window size
- **Interactive Selection**: Checkboxes for dataset selection, radio buttons for baseline selection

### Analysis Capabilities
- **Baseline Comparison Modes**:
  - Single: Compare all datasets to one baseline
  - Row: Compare datasets with same thread count
  - Column: Compare datasets with same simulation count
- **Performance Visualization**: Overlaid bar charts showing function performance ratios
- **Real-time Statistics**: Detailed analysis panel with performance metrics
- **Chart Export**: Save charts as PNG, PDF, or SVG files
- **Function Filtering**: Click chart bars to select/deselect specific functions

## Usage

### 1. Load Project Data

**Automatic Loading** (Easiest):
- Simply launch the application
- If `energyplus_project.json` exists in the current directory, it will auto-load
- All 42 datasets will be loaded automatically

**Manual Loading**:
- Use any of these methods:
  - Click "📁 Load Project" in the toolbar
  - Use menu: File → Load Project... 
  - Press Ctrl+O keyboard shortcut
- Select the `energyplus_project.json` file
- Application will load all referenced simulation datasets

### 2. Select Datasets for Analysis
- Use checkboxes in the matrix to select datasets for comparison
- Each cell shows: execution time, selection checkbox, baseline radio button
- Quick selection options:
  - "→ Select Row" button: Select all datasets with same thread count
  - "↓ Select Column" button: Select all datasets with same simulation count
  - Menu: Analysis → Clear All Selections (or Ctrl+D)

### 3. Set Baseline for Comparison
- Choose baseline mode using toolbar radio buttons or Analysis menu:
  - **Single**: Compare all to one specific dataset
  - **Row**: Compare datasets within same thread count
  - **Column**: Compare datasets within same simulation count
- Select appropriate baseline using radio buttons in the matrix

### 4. Analyze Results
- Click "📊 Update Chart" (or press F5) to visualize selected datasets
- View real-time statistics in the right panel
- Toggle display options:
  - Show/hide function labels on chart
  - Show/hide statistics panel
- Export results: "💾 Export Chart" (or Ctrl+S) for PNG, PDF, or SVG

## Project File Structure

The `energyplus_project.json` file organizes all simulation data:

```json
{
  "project_info": {
    "name": "EnergyPlus Concurrent Simulation Performance Analysis",
    "description": "Performance profiling data...",
    "building_type": "Commercial Office",
    "climate_zone": "4A"
  },
  "datasets": {
    "1_sim": {
      "1_thread": "energyplus_concurrent_01sims_01threads.json",
      "2_threads": "energyplus_concurrent_01sims_02threads.json",
      ...
    },
    ...
  }
}
```

## Dataset Coverage

- **Thread Counts**: 1, 2, 4, 8, 16, 32 threads
- **Concurrent Simulations**: 1, 2, 4, 8, 16, 32, 64 simulations  
- **Total Datasets**: 42 complete performance profiles
- **Functions Tracked**: 20+ EnergyPlus functions per dataset

## Performance Insights

The tool helps identify:
- Optimal threading configurations for different workloads
- Resource contention effects with concurrent simulations
- Function-level performance variations
- Memory and CPU utilization patterns
- Performance scaling characteristics

## Example Analysis Workflows

### Threading Efficiency Analysis
1. Set baseline mode to "Column" 
2. Select a simulation count (e.g., 4 simulations)
3. Compare how performance varies with thread count
4. Identify optimal thread count for that workload

### Concurrency Impact Analysis  
1. Set baseline mode to "Row"
2. Select a thread count (e.g., 8 threads)
3. Compare how performance varies with concurrent simulations
4. Identify when resource contention becomes significant

### Function-Specific Analysis
1. Load data and select multiple datasets
2. Click on specific function bars in the chart
3. View function-specific performance ranges in statistics panel
4. Identify functions most affected by threading/concurrency changes

## Technical Details

- **Built with**: Python, tkinter, matplotlib, pandas, numpy
- **Data Format**: JSON files with function-level timing data
- **Visualization**: Overlaid bar charts with performance ratios
- **Real-time Analysis**: Dynamic statistics calculation and display