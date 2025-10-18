"""
Comparison visualization script for EnergyPlus baseline vs contended profiling data
Creates a single bar chart showing performance degradation across all functions
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class EnergyPlusComparisonVisualizer:
    """
    Compares baseline and contended EnergyPlus profiling data
    Creates visualization showing performance impact of memory contention
    """
    
    def __init__(self, baseline_file="energyplus_profiling_data.json", 
                 contended_file="energyplus_profiling_contended.json"):
        self.baseline_file = baseline_file
        self.contended_file = contended_file
        self.baseline_data = None
        self.contended_data = None
        self.comparison_data = {}
        
    def load_data(self):
        """Load both baseline and contended profiling data"""
        try:
            with open(self.baseline_file, 'r') as f:
                self.baseline_data = json.load(f)
            print(f"Loaded baseline data from {self.baseline_file}")
        except FileNotFoundError:
            print(f"Baseline file {self.baseline_file} not found")
            return False
            
        try:
            with open(self.contended_file, 'r') as f:
                self.contended_data = json.load(f)
            print(f"Loaded contended data from {self.contended_file}")
        except FileNotFoundError:
            print(f"Contended file {self.contended_file} not found")
            return False
            
        return True
    
    def prepare_comparison_data(self):
        """Prepare data for comparison visualization"""
        if not self.baseline_data or not self.contended_data:
            return False
            
        baseline_functions = self.baseline_data['functions']
        contended_functions = self.contended_data['functions']
        
        # Find common functions between both datasets
        common_functions = set(baseline_functions.keys()) & set(contended_functions.keys())
        
        comparison_results = []
        
        for func_name in common_functions:
            baseline_time = baseline_functions[func_name]['total_time']
            contended_time = contended_functions[func_name]['total_time']
            
            # Calculate normalized performance impact
            # Baseline is normalized to 1.0, contended shows the multiplier
            if baseline_time > 0:
                performance_ratio = contended_time / baseline_time
                degradation_percent = ((contended_time - baseline_time) / baseline_time) * 100
            else:
                performance_ratio = 1.0
                degradation_percent = 0.0
            
            comparison_results.append({
                'function': func_name,
                'baseline_time': baseline_time,
                'contended_time': contended_time,
                'performance_ratio': performance_ratio,
                'degradation_percent': degradation_percent,
                'baseline_calls': baseline_functions[func_name]['call_count'],
                'contended_calls': contended_functions[func_name]['call_count']
            })
        
        # Sort by degradation percentage (most impacted first)
        comparison_results.sort(key=lambda x: x['degradation_percent'], reverse=True)
        
        self.comparison_data = comparison_results
        return True
    
    def create_comparison_chart(self, show_baseline_bars=True):
        """Create a comprehensive bar chart comparing baseline vs contended performance"""
        if not self.comparison_data:
            return
        
        # Set up the figure with a large size for readability
        plt.figure(figsize=(16, 12))
        
        # Extract data for plotting
        function_names = [item['function'] for item in self.comparison_data]
        baseline_normalized = [1.0] * len(function_names)  # All baseline values normalized to 1.0
        contended_ratios = [item['performance_ratio'] for item in self.comparison_data]
        degradation_percents = [item['degradation_percent'] for item in self.comparison_data]
        
        # Shorten function names for better readability
        short_names = []
        for name in function_names:
            if len(name) > 25:
                # Remove common prefixes and shorten
                short_name = name.replace('Calc', '').replace('Simulate', 'Sim').replace('Manager', 'Mgr')
                if len(short_name) > 25:
                    short_name = short_name[:22] + '...'
                short_names.append(short_name)
            else:
                short_names.append(name)
        
        # Create positions for bars
        x_pos = np.arange(len(function_names))
        
        # Create the bar chart
        fig, ax = plt.subplots(figsize=(20, 12))
        
        # Plot contended bars with color coding based on severity
        colors = []
        for ratio in contended_ratios:
            if ratio < 1.5:
                colors.append('#FFA500')  # Orange for mild impact
            elif ratio < 3.0:
                colors.append('#FF4500')  # Red-orange for moderate impact
            elif ratio < 5.0:
                colors.append('#DC143C')  # Crimson for severe impact
            else:
                colors.append('#8B0000')  # Dark red for extreme impact
        
        if show_baseline_bars:
            # Plot baseline bars (all at 1.0, normalized)
            baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4, 
                                  label='Baseline (Normalized)', 
                                  color='#2E8B57', alpha=0.8)
            
            contended_bars = ax.bar(x_pos + 0.2, contended_ratios, 0.4,
                                   label='Memory Contended',
                                   color=colors, alpha=0.8)
        else:
            # Plot only contended bars, centered
            contended_bars = ax.bar(x_pos, contended_ratios, 0.6,
                                   label='Memory Contended',
                                   color=colors, alpha=0.8)
        
        # Customize the chart
        ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
        ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold')
        ax.set_title('EnergyPlus Performance Impact: Baseline vs Memory Contention\n' +
                    f'Overall System Degradation: {self.contended_data["summary"]["overall_performance_degradation_percent"]:.1f}%',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Set x-axis labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
        
        # Add horizontal line at y=1.0 for reference (always show for context)
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add value labels on top of contended bars for high-impact functions
        for i, (bar, ratio, degradation) in enumerate(zip(contended_bars, contended_ratios, degradation_percents)):
            if degradation > 100:  # Only label functions with >100% degradation
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{ratio:.1f}x\n(+{degradation:.0f}%)',
                       ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # Customize legend
        ax.legend(loc='upper left', fontsize=11)
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set y-axis to start from 0 and add some padding at the top
        max_ratio = max(contended_ratios)
        ax.set_ylim(0, max_ratio * 1.15)
        
        # Add color legend for severity levels
        from matplotlib.patches import Patch
        severity_legend = [
            Patch(color='#FFA500', label='Mild Impact (1.0-1.5x)'),
            Patch(color='#FF4500', label='Moderate Impact (1.5-3.0x)'),
            Patch(color='#DC143C', label='Severe Impact (3.0-5.0x)'),
            Patch(color='#8B0000', label='Extreme Impact (>5.0x)')
        ]
        
        # Add second legend for severity
        second_legend = ax.legend(handles=severity_legend, loc='upper right', 
                                title='Impact Severity', fontsize=10)
        ax.add_artist(second_legend)  # Add back the first legend
        ax.legend(loc='upper left', fontsize=11)
        
        # Add system information as text box
        system_info = (
            f"System Conditions:\n"
            f"• Memory Pressure: {self.contended_data['metadata']['system_conditions']['memory_pressure']}\n"
            f"• Available Memory: {self.contended_data['metadata']['system_conditions']['available_memory']}\n"
            f"• Cache Hit Ratio: {self.contended_data['metadata']['system_conditions']['cache_hit_ratio']}\n"
            f"• Swap Activity: {self.contended_data['metadata']['system_conditions']['swap_activity']}"
        )
        
        ax.text(0.02, 0.98, system_info, transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart with appropriate filename
        if show_baseline_bars:
            filename = 'energyplus_baseline_vs_contended_comparison.png'
        else:
            filename = 'energyplus_contended_only_comparison.png'
            
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        
        print(f"Comparison chart saved as '{filename}'")
        
        # Display summary statistics
        self.print_comparison_summary()
        
        plt.show()
    
    def print_comparison_summary(self):
        """Print summary statistics of the comparison"""
        if not self.comparison_data:
            return
        
        print("\n" + "="*80)
        print("PERFORMANCE COMPARISON SUMMARY")
        print("="*80)
        
        total_baseline = sum(item['baseline_time'] for item in self.comparison_data)
        total_contended = sum(item['contended_time'] for item in self.comparison_data)
        overall_degradation = ((total_contended - total_baseline) / total_baseline) * 100
        
        print(f"Total Baseline Time: {total_baseline:.2f} seconds")
        print(f"Total Contended Time: {total_contended:.2f} seconds")
        print(f"Overall Performance Degradation: {overall_degradation:.1f}%")
        print(f"Additional Time Due to Contention: {total_contended - total_baseline:.2f} seconds")
        
        print(f"\nTop 10 Most Impacted Functions:")
        print("-" * 60)
        for i, item in enumerate(self.comparison_data[:10], 1):
            print(f"{i:2d}. {item['function']:<35} "
                  f"{item['performance_ratio']:>5.1f}x (+{item['degradation_percent']:>6.1f}%)")
        
        # Statistics
        ratios = [item['performance_ratio'] for item in self.comparison_data]
        print(f"\nPerformance Ratio Statistics:")
        print(f"  Average: {np.mean(ratios):.2f}x")
        print(f"  Median: {np.median(ratios):.2f}x")
        print(f"  Maximum: {np.max(ratios):.2f}x")
        print(f"  Minimum: {np.min(ratios):.2f}x")
        
        # Count functions by impact severity
        mild = sum(1 for r in ratios if 1.0 <= r < 1.5)
        moderate = sum(1 for r in ratios if 1.5 <= r < 3.0)
        severe = sum(1 for r in ratios if 3.0 <= r < 5.0)
        extreme = sum(1 for r in ratios if r >= 5.0)
        
        print(f"\nImpact Distribution:")
        print(f"  Mild Impact (1.0-1.5x): {mild} functions")
        print(f"  Moderate Impact (1.5-3.0x): {moderate} functions")
        print(f"  Severe Impact (3.0-5.0x): {severe} functions")
        print(f"  Extreme Impact (>5.0x): {extreme} functions")


def main():
    """Main function to run the comparison visualization"""
    visualizer = EnergyPlusComparisonVisualizer()
    
    if visualizer.load_data():
        if visualizer.prepare_comparison_data():
            # Create chart with baseline bars (default)
            visualizer.create_comparison_chart(show_baseline_bars=True)
            
            # Uncomment the line below to create a version without baseline bars
            # visualizer.create_comparison_chart(show_baseline_bars=False)
        else:
            print("Failed to prepare comparison data")
    else:
        print("Failed to load data files. Please ensure both baseline and contended data files exist.")


if __name__ == "__main__":
    main()