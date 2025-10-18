#!/usr/bin/env python3
"""
Test script to verify real data visualization capabilities
"""

import json
import os

def test_data_loading():
    """Test that the project file and datasets are properly structured"""
    
    print("Testing EnergyPlus Concurrent Simulation Data Loading")
    print("="*55)
    
    # Check project file
    project_file = "energyplus_project.json"
    if not os.path.exists(project_file):
        print(f"❌ Project file {project_file} not found!")
        return
    
    print(f"✅ Project file {project_file} found")
    
    # Load and validate project structure
    with open(project_file, 'r') as f:
        project_data = json.load(f)
    
    print(f"✅ Project loaded: {project_data['project_info']['name']}")
    
    # Check datasets
    datasets = project_data.get('datasets', {})
    total_files = 0
    loaded_files = 0
    
    print("\nChecking individual dataset files:")
    print("-" * 40)
    
    for sim_count, thread_data in datasets.items():
        for thread_count, filename in thread_data.items():
            total_files += 1
            
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        data = json.load(f)
                    
                    # Validate data structure
                    metadata = data.get('metadata', {})
                    functions = data.get('functions', {})
                    
                    total_time = metadata.get('total_simulation_time', 0)
                    function_count = len(functions)
                    
                    loaded_files += 1
                    
                    # Print every 7th file to avoid spam
                    if total_files % 7 == 1:
                        print(f"✅ {filename}: {total_time:.1f}s, {function_count} functions")
                    
                except Exception as e:
                    print(f"❌ {filename}: Error - {e}")
            else:
                print(f"❌ {filename}: Not found")
    
    print(f"\nSummary:")
    print(f"Total expected files: {total_files}")
    print(f"Successfully loaded: {loaded_files}")
    print(f"Success rate: {loaded_files/total_files*100:.1f}%")
    
    if loaded_files >= 30:
        print("✅ Sufficient data for visualization!")
    else:
        print("⚠️  Limited data available")
    
    # Test function analysis
    print(f"\nFunction Analysis Example:")
    print("-" * 30)
    
    # Load a sample file
    sample_file = "energyplus_concurrent_01sims_01threads.json"
    if os.path.exists(sample_file):
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)
        
        functions = sample_data.get('functions', {})
        
        print(f"Sample dataset: {sample_file}")
        print(f"Total simulation time: {sample_data['metadata']['total_simulation_time']:.1f}s")
        print(f"Functions tracked: {len(functions)}")
        print("\nTop 5 most time-consuming functions:")
        
        # Sort functions by total time
        sorted_functions = sorted(functions.items(), 
                                key=lambda x: x[1]['total_time'], 
                                reverse=True)
        
        for i, (func_name, func_data) in enumerate(sorted_functions[:5]):
            time = func_data['total_time']
            percentage = func_data['percentage_of_total']
            print(f"{i+1}. {func_name}: {time:.2f}s ({percentage:.1f}%)")

if __name__ == "__main__":
    test_data_loading()