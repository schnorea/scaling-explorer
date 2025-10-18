"""
Fixed version of visualization scripts that avoids figure display issues
Uses Agg backend and focuses on PNG file generation only
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import json
import numpy as np

def create_all_visualizations():
    """Create all comparison visualizations without display issues"""
    
    print("Creating all EnergyPlus performance comparison visualizations...")
    print("Using Agg backend for reliable PNG generation")
    
    # Clear any existing figures
    plt.close('all')
    
    # 1. Memory Contention Comparison
    print("\n1. Creating Memory Contention Comparison...")
    try:
        from energyplus_comparison_viz import EnergyPlusComparisonVisualizer
        
        viz1 = EnergyPlusComparisonVisualizer()
        if viz1.load_data() and viz1.prepare_comparison_data():
            create_contention_chart(viz1)
            print("✅ Memory contention visualization completed")
        else:
            print("❌ Failed to create memory contention visualization")
    except Exception as e:
        print(f"❌ Error in memory contention visualization: {e}")
    
    # 2. Multithreaded Comparison  
    print("\n2. Creating Multithreaded Comparison...")
    try:
        from energyplus_multithreaded_comparison_viz import EnergyPlusMultithreadedComparisonVisualizer
        
        viz2 = EnergyPlusMultithreadedComparisonVisualizer()
        if viz2.load_data() and viz2.prepare_comparison_data():
            create_multithreaded_chart(viz2)
            print("✅ Multithreaded visualization completed")
        else:
            print("❌ Failed to create multithreaded visualization")
    except Exception as e:
        print(f"❌ Error in multithreaded visualization: {e}")
    
    # 3. Hybrid Comparison
    print("\n3. Creating Hybrid Comparison...")
    try:
        from energyplus_hybrid_comparison_viz import EnergyPlusHybridComparisonVisualizer
        
        viz3 = EnergyPlusHybridComparisonVisualizer()
        if viz3.load_data() and viz3.prepare_comparison_data():
            create_hybrid_chart(viz3)
            print("✅ Hybrid visualization completed")
        else:
            print("❌ Failed to create hybrid visualization")
    except Exception as e:
        print(f"❌ Error in hybrid visualization: {e}")
    
    print("\n" + "="*60)
    print("ALL VISUALIZATIONS COMPLETE")
    print("="*60)
    print("Generated PNG files:")
    print("• energyplus_baseline_vs_contended_fixed.png")  
    print("• energyplus_baseline_vs_multithreaded_fixed.png")
    print("• energyplus_baseline_vs_hybrid_fixed.png")

def create_contention_chart(visualizer):
    """Create memory contention chart without display issues"""
    plt.style.use('default')  # Reset style
    
    # Extract data
    function_names = [item['function'] for item in visualizer.comparison_data]
    baseline_normalized = [1.0] * len(function_names)
    contended_ratios = [item['performance_ratio'] for item in visualizer.comparison_data]
    degradation_percents = [item['degradation_percent'] for item in visualizer.comparison_data]
    
    # Shorten names
    short_names = [name[:20] + '...' if len(name) > 20 else name for name in function_names]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))
    
    x_pos = np.arange(len(function_names))
    
    # Color coding
    colors = []
    for ratio in contended_ratios:
        if ratio < 1.5:
            colors.append('#FFA500')
        elif ratio < 3.0:
            colors.append('#FF4500')
        elif ratio < 5.0:
            colors.append('#DC143C')
        else:
            colors.append('#8B0000')
    
    # Plot bars
    baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4, 
                          label='Baseline (Normalized)', color='#2E8B57', alpha=0.8)
    contended_bars = ax.bar(x_pos + 0.2, contended_ratios, 0.4,
                           label='Memory Contended', color=colors, alpha=0.8)
    
    # Customize
    ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
    ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold')
    ax.set_title('EnergyPlus Performance: Baseline vs Memory Contention', 
                fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
    ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Add labels for high-impact functions
    for i, (bar, ratio, degradation) in enumerate(zip(contended_bars, contended_ratios, degradation_percents)):
        if degradation > 100:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{ratio:.1f}x', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('energyplus_baseline_vs_contended_fixed.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_multithreaded_chart(visualizer):
    """Create multithreaded chart without display issues"""
    plt.style.use('default')
    
    # Extract data
    function_names = [item['function'] for item in visualizer.comparison_data]
    baseline_normalized = [1.0] * len(function_names)
    multithreaded_ratios = [item['performance_ratio'] for item in visualizer.comparison_data]
    improvement_percents = [item['improvement_percent'] for item in visualizer.comparison_data]
    
    # Shorten names
    short_names = [name[:20] + '...' if len(name) > 20 else name for name in function_names]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))
    
    x_pos = np.arange(len(function_names))
    
    # Color coding for improvements
    colors = []
    for ratio in multithreaded_ratios:
        if ratio > 0.9:
            colors.append('#FFB6C1')  # Minimal improvement
        elif ratio > 0.7:
            colors.append('#87CEEB')  # Moderate improvement  
        elif ratio > 0.5:
            colors.append('#98FB98')  # Good improvement
        elif ratio > 0.3:
            colors.append('#00CED1')  # Great improvement
        else:
            colors.append('#32CD32')  # Excellent improvement
    
    # Plot bars
    baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4,
                          label='Baseline (Normalized)', color='#2E8B57', alpha=0.8)
    multithreaded_bars = ax.bar(x_pos + 0.2, multithreaded_ratios, 0.4,
                               label='Multithreaded', color=colors, alpha=0.8)
    
    # Customize
    ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
    ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold') 
    ax.set_title('EnergyPlus Performance: Baseline vs Selective Multithreading',
                fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
    ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1.1)
    
    # Add labels for high-improvement functions
    for i, (bar, ratio, improvement) in enumerate(zip(multithreaded_bars, multithreaded_ratios, improvement_percents)):
        if improvement > 30:
            height = bar.get_height()
            speedup = 1.0 / ratio if ratio > 0 else 1.0
            ax.text(bar.get_x() + bar.get_width()/2., height - 0.05,
                   f'{speedup:.1f}x', ha='center', va='top', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('energyplus_baseline_vs_multithreaded_fixed.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_hybrid_chart(visualizer):
    """Create hybrid chart without display issues"""
    plt.style.use('default')
    
    # Extract data
    function_names = [item['function'] for item in visualizer.comparison_data]
    baseline_normalized = [1.0] * len(function_names)
    hybrid_ratios = [item['performance_ratio'] for item in visualizer.comparison_data]
    net_change_percents = [item['net_change_percent'] for item in visualizer.comparison_data]
    net_effects = [item['net_effect'] for item in visualizer.comparison_data]
    
    # Shorten names
    short_names = [name[:20] + '...' if len(name) > 20 else name for name in function_names]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(18, 10))
    
    x_pos = np.arange(len(function_names))
    
    # Color coding by net effect
    colors = []
    for ratio, effect in zip(hybrid_ratios, net_effects):
        if effect == 'gain':
            colors.append('#228B22' if ratio < 0.85 else '#90EE90')
        elif effect == 'mixed':
            colors.append('#4169E1' if ratio < 1.0 else '#8A2BE2')
        elif effect in ['loss', 'slight_loss']:
            if ratio > 2.0:
                colors.append('#8B0000')
            elif ratio > 1.5:
                colors.append('#DC143C')
            else:
                colors.append('#FF6347')
        else:
            colors.append('#FFD700')
    
    # Plot bars
    baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4,
                          label='Baseline (Normalized)', color='#2E8B57', alpha=0.8)
    hybrid_bars = ax.bar(x_pos + 0.2, hybrid_ratios, 0.4,
                        label='Hybrid (Threading + Contention)', color=colors, alpha=0.8)
    
    # Customize
    ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
    ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold')
    ax.set_title('EnergyPlus Performance: Baseline vs Multithreading with Memory Contention',
                fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
    ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Add labels for significant changes
    for i, (bar, ratio, net_change) in enumerate(zip(hybrid_bars, hybrid_ratios, net_change_percents)):
        if abs(net_change) > 30:
            height = bar.get_height()
            if net_change > 0:
                label_text = f'{ratio:.1f}x'
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       label_text, ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('energyplus_baseline_vs_hybrid_fixed.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

if __name__ == "__main__":
    create_all_visualizations()