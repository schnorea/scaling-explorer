"""
Demo script showing how to generate charts with and without baseline bars
"""

from energyplus_comparison_viz import EnergyPlusComparisonVisualizer
from energyplus_multithreaded_comparison_viz import EnergyPlusMultithreadedComparisonVisualizer

def generate_all_chart_variations():
    """Generate all possible chart variations"""
    
    print("="*60)
    print("GENERATING MEMORY CONTENTION COMPARISON CHARTS")
    print("="*60)
    
    # Memory contention comparisons
    contention_viz = EnergyPlusComparisonVisualizer()
    if contention_viz.load_data() and contention_viz.prepare_comparison_data():
        print("\n1. Creating chart WITH baseline bars...")
        contention_viz.create_comparison_chart(show_baseline_bars=True)
        
        print("\n2. Creating chart WITHOUT baseline bars...")
        contention_viz.create_comparison_chart(show_baseline_bars=False)
    else:
        print("Failed to load contention data")
    
    print("\n" + "="*60)
    print("GENERATING MULTITHREADED COMPARISON CHARTS")
    print("="*60)
    
    # Multithreaded comparisons
    threading_viz = EnergyPlusMultithreadedComparisonVisualizer()
    if threading_viz.load_data() and threading_viz.prepare_comparison_data():
        print("\n1. Creating chart WITH baseline bars...")
        threading_viz.create_comparison_chart(show_baseline_bars=True)
        
        print("\n2. Creating chart WITHOUT baseline bars...")
        threading_viz.create_comparison_chart(show_baseline_bars=False)
    else:
        print("Failed to load multithreaded data")
    
    print("\n" + "="*60)
    print("CHART GENERATION COMPLETE")
    print("="*60)
    print("Generated files:")
    print("• energyplus_baseline_vs_contended_comparison.png (with baseline)")
    print("• energyplus_contended_only_comparison.png (without baseline)")
    print("• energyplus_baseline_vs_multithreaded_comparison.png (with baseline)")
    print("• energyplus_multithreaded_only_comparison.png (without baseline)")

if __name__ == "__main__":
    generate_all_chart_variations()