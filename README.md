# EnergyPlus Concurrent Simulation Explorer

A GUI application for analyzing and visualizing EnergyPlus simulation performance data across different threading and concurrency configurations.

## Features

### Data Management
- **Project File Loading**: Load all simulation datasets with a single project JSON file
- **Real Data Visualization**: Display actual EnergyPlus function performance data
- **Matrix Layout**: 7×6 grid showing thread counts (1-32) vs concurrent simulations (1-64)

### Analysis Capabilities
- **Baseline Comparison Modes**:
  - Single: Compare all datasets to one baseline
  - Row: Compare datasets with same thread count
  - Column: Compare datasets with same simulation count
- **Performance Visualization**: Overlaid bar charts showing function performance ratios
- **Real-time Statistics**: Detailed analysis panel with performance metrics

### User Interface
- **Resizable Panels**: Adjustable chart and data selection areas
- **Scrollable Content**: Full access to all datasets regardless of window size
- **Interactive Selection**: Checkboxes for dataset selection, radio buttons for baseline selection
- **Function Filtering**: Click chart bars to select/deselect specific functions

## Usage

### 1. Load Project Data
1. Launch the application
2. Click "Load Project Data" button
3. Select the `energyplus_project.json` file
4. Application will load all 42 simulation datasets

### 2. Select Datasets for Analysis
- Use checkboxes in the matrix to select datasets for comparison
- Each cell shows: execution time, selection checkbox, baseline radio button
- Use "Select Row" or "Select Column" for quick selections

### 3. Set Baseline for Comparison
- Choose baseline mode: Single, Row, or Column
- Select appropriate baseline using radio buttons
- Baseline determines what performance ratios are calculated against

### 4. Analyze Results
- Click "Update Chart" to visualize selected datasets
- View real-time statistics in the right panel
- Toggle function labels and statistics panel as needed

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