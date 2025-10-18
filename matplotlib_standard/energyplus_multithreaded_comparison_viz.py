"""
Comparison visualization script for EnergyPlus baseline vs multithreaded profiling data
Creates a single bar chart showing performance improvements across all functions
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class EnergyPlusMultithreadedComparisonVisualizer:
    """
    Compares baseline and multithreaded EnergyPlus profiling data
    Creates visualization showing performance improvements from selective multithreading
    """
    
    def __init__(self, baseline_file="energyplus_profiling_data.json", 
                 multithreaded_file="energyplus_profiling_multithreaded.json"):
        self.baseline_file = baseline_file
        self.multithreaded_file = multithreaded_file
        self.baseline_data = None
        self.multithreaded_data = None
        self.comparison_data = {}
        
    def load_data(self):
        """Load both baseline and multithreaded profiling data"""
        try:
            with open(self.baseline_file, 'r') as f:
                self.baseline_data = json.load(f)
            print(f"Loaded baseline data from {self.baseline_file}")
        except FileNotFoundError:
            print(f"Baseline file {self.baseline_file} not found")
            return False
            
        try:
            with open(self.multithreaded_file, 'r') as f:
                self.multithreaded_data = json.load(f)
            print(f"Loaded multithreaded data from {self.multithreaded_file}")
        except FileNotFoundError:
            print(f"Multithreaded file {self.multithreaded_file} not found")
            return False
            
        return True
    
    def prepare_comparison_data(self):
        """Prepare data for comparison visualization"""
        if not self.baseline_data or not self.multithreaded_data:
            return False
            
        baseline_functions = self.baseline_data['functions']
        multithreaded_functions = self.multithreaded_data['functions']
        
        # Find common functions between both datasets
        common_functions = set(baseline_functions.keys()) & set(multithreaded_functions.keys())
        
        comparison_results = []
        
        for func_name in common_functions:
            baseline_time = baseline_functions[func_name]['total_time']
            multithreaded_time = multithreaded_functions[func_name]['total_time']
            
            # Calculate normalized performance improvement
            # Baseline is normalized to 1.0, multithreaded shows the fraction (improvement)
            if baseline_time > 0:
                performance_ratio = multithreaded_time / baseline_time
                improvement_percent = ((baseline_time - multithreaded_time) / baseline_time) * 100
                speedup_factor = baseline_time / multithreaded_time
            else:
                performance_ratio = 1.0
                improvement_percent = 0.0
                speedup_factor = 1.0
            
            # Get threading metrics if available
            threading_metrics = multithreaded_functions[func_name].get('threading_metrics', {})
            
            comparison_results.append({
                'function': func_name,
                'baseline_time': baseline_time,
                'multithreaded_time': multithreaded_time,
                'performance_ratio': performance_ratio,  # Lower is better (fraction of original time)
                'improvement_percent': improvement_percent,
                'speedup_factor': speedup_factor,
                'baseline_calls': baseline_functions[func_name]['call_count'],
                'multithreaded_calls': multithreaded_functions[func_name]['call_count'],
                'thread_efficiency': threading_metrics.get('thread_efficiency', 0.0),
                'time_saved': threading_metrics.get('time_saved', 0.0)
            })
        
        # Sort by improvement percentage (most improved first)
        comparison_results.sort(key=lambda x: x['improvement_percent'], reverse=True)
        
        self.comparison_data = comparison_results
        return True
    
    def create_comparison_chart(self, show_baseline_bars=True):
        """Create a comprehensive bar chart comparing baseline vs multithreaded performance"""
        if not self.comparison_data:
            return
        
        # Set up the figure with a large size for readability
        plt.figure(figsize=(16, 12))
        
        # Extract data for plotting
        function_names = [item['function'] for item in self.comparison_data]
        baseline_normalized = [1.0] * len(function_names)  # All baseline values normalized to 1.0
        multithreaded_ratios = [item['performance_ratio'] for item in self.comparison_data]
        improvement_percents = [item['improvement_percent'] for item in self.comparison_data]
        
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
        
        # Plot multithreaded bars with color coding based on improvement level
        colors = []
        for ratio in multithreaded_ratios:
            if ratio > 0.9:  # Little to no improvement
                colors.append('#FFB6C1')  # Light pink
            elif ratio > 0.7:  # Moderate improvement
                colors.append('#87CEEB')  # Sky blue
            elif ratio > 0.5:  # Good improvement
                colors.append('#98FB98')  # Pale green
            elif ratio > 0.3:  # Great improvement
                colors.append('#00CED1')  # Dark turquoise
            else:  # Excellent improvement
                colors.append('#32CD32')  # Lime green
        
        if show_baseline_bars:
            # Plot baseline bars (all at 1.0, normalized)
            baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4, 
                                  label='Baseline (Normalized)', 
                                  color='#2E8B57', alpha=0.8)
            
            multithreaded_bars = ax.bar(x_pos + 0.2, multithreaded_ratios, 0.4,
                                       label='Multithreaded',
                                       color=colors, alpha=0.8)
        else:
            # Plot only multithreaded bars, centered
            multithreaded_bars = ax.bar(x_pos, multithreaded_ratios, 0.6,
                                       label='Multithreaded',
                                       color=colors, alpha=0.8)
        
        # Customize the chart
        ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
        ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold')
        ax.set_title('EnergyPlus Performance Improvement: Baseline vs Selective Multithreading\n' +
                    f'Overall Speedup: {self.multithreaded_data["summary"]["overall_speedup_factor"]:.2f}x ' +
                    f'({self.multithreaded_data["summary"]["overall_performance_improvement_percent"]:.1f}% improvement)',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Set x-axis labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
        
        # Add horizontal line at y=1.0 for reference (always show for context)
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add value labels on top of multithreaded bars for high-improvement functions
        for i, (bar, ratio, improvement) in enumerate(zip(multithreaded_bars, multithreaded_ratios, improvement_percents)):
            if improvement > 30:  # Only label functions with >30% improvement
                height = bar.get_height()
                speedup = 1.0 / ratio if ratio > 0 else 1.0
                ax.text(bar.get_x() + bar.get_width()/2., height - 0.05,
                       f'{speedup:.1f}x\n(-{improvement:.0f}%)',
                       ha='center', va='top', fontsize=8, fontweight='bold')
        
        # Customize legend
        ax.legend(loc='upper right', fontsize=11)
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set y-axis to show improvement (lower values are better)
        ax.set_ylim(0, 1.1)
        
        # Add color legend for improvement levels
        from matplotlib.patches import Patch
        improvement_legend = [
            Patch(color='#FFB6C1', label='Minimal (<10% improvement)'),
            Patch(color='#87CEEB', label='Moderate (10-30% improvement)'),
            Patch(color='#98FB98', label='Good (30-50% improvement)'),
            Patch(color='#00CED1', label='Great (50-70% improvement)'),
            Patch(color='#32CD32', label='Excellent (>70% improvement)')
        ]
        
        # Add second legend for improvement levels
        second_legend = ax.legend(handles=improvement_legend, loc='upper left', 
                                title='Improvement Level', fontsize=10)
        ax.add_artist(second_legend)  # Add back the first legend
        ax.legend(loc='upper right', fontsize=11)
        
        # Add system information as text box
        system_info = (
            f"System Configuration:\n"
            f"• CPU Cores: {self.multithreaded_data['metadata']['system_conditions']['cpu_cores']}\n"
            f"• Thread Pool: {self.multithreaded_data['metadata']['system_conditions']['thread_pool_size']} threads\n"
            f"• Memory Pressure: {self.multithreaded_data['metadata']['system_conditions']['memory_pressure']}\n"
            f"• Cache Hit Ratio: {self.multithreaded_data['metadata']['system_conditions']['cache_hit_ratio']}"
        )
        
        ax.text(0.02, 0.02, system_info, transform=ax.transAxes, fontsize=9,
               verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart with appropriate filename
        if show_baseline_bars:
            filename = 'energyplus_baseline_vs_multithreaded_comparison.png'
        else:
            filename = 'energyplus_multithreaded_only_comparison.png'
            
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        
        print(f"Multithreaded comparison chart saved as '{filename}'")
        
        # Display summary statistics
        self.print_comparison_summary()
        
        plt.show()
    
    def print_comparison_summary(self):
        """Print summary statistics of the comparison"""
        if not self.comparison_data:
            return
        
        print("\n" + "="*80)
        print("MULTITHREADING PERFORMANCE COMPARISON SUMMARY")
        print("="*80)
        
        total_baseline = sum(item['baseline_time'] for item in self.comparison_data)
        total_multithreaded = sum(item['multithreaded_time'] for item in self.comparison_data)
        overall_improvement = ((total_baseline - total_multithreaded) / total_baseline) * 100
        overall_speedup = total_baseline / total_multithreaded
        
        print(f"Total Baseline Time: {total_baseline:.2f} seconds")
        print(f"Total Multithreaded Time: {total_multithreaded:.2f} seconds")
        print(f"Overall Performance Improvement: {overall_improvement:.1f}%")
        print(f"Overall Speedup Factor: {overall_speedup:.2f}x")
        print(f"Time Saved Through Multithreading: {total_baseline - total_multithreaded:.2f} seconds")
        
        print(f"\nTop 10 Most Improved Functions:")
        print("-" * 70)
        for i, item in enumerate(self.comparison_data[:10], 1):
            print(f"{i:2d}. {item['function']:<35} "
                  f"{item['speedup_factor']:>5.1f}x (-{item['improvement_percent']:>5.1f}%) "
                  f"-{item['time_saved']:>6.2f}s")
        
        # Statistics
        improvements = [item['improvement_percent'] for item in self.comparison_data if item['improvement_percent'] > 0]
        speedups = [item['speedup_factor'] for item in self.comparison_data if item['speedup_factor'] > 1.0]
        
        if improvements:
            print(f"\nImprovement Statistics (for functions that benefited):")
            print(f"  Average Improvement: {np.mean(improvements):.1f}%")
            print(f"  Median Improvement: {np.median(improvements):.1f}%")
            print(f"  Maximum Improvement: {np.max(improvements):.1f}%")
            print(f"  Average Speedup: {np.mean(speedups):.2f}x")
            print(f"  Maximum Speedup: {np.max(speedups):.2f}x")
        
        # Count functions by improvement level
        minimal = sum(1 for item in self.comparison_data if 0 <= item['improvement_percent'] < 10)
        moderate = sum(1 for item in self.comparison_data if 10 <= item['improvement_percent'] < 30)
        good = sum(1 for item in self.comparison_data if 30 <= item['improvement_percent'] < 50)
        great = sum(1 for item in self.comparison_data if 50 <= item['improvement_percent'] < 70)
        excellent = sum(1 for item in self.comparison_data if item['improvement_percent'] >= 70)
        
        print(f"\nImprovement Distribution:")
        print(f"  Minimal Improvement (<10%): {minimal} functions")
        print(f"  Moderate Improvement (10-30%): {moderate} functions")
        print(f"  Good Improvement (30-50%): {good} functions")
        print(f"  Great Improvement (50-70%): {great} functions")
        print(f"  Excellent Improvement (≥70%): {excellent} functions")
        
        # Threading efficiency analysis
        high_efficiency = sum(1 for item in self.comparison_data if item['thread_efficiency'] >= 0.8)
        medium_efficiency = sum(1 for item in self.comparison_data if 0.5 <= item['thread_efficiency'] < 0.8)
        low_efficiency = sum(1 for item in self.comparison_data if 0 < item['thread_efficiency'] < 0.5)
        no_threading = sum(1 for item in self.comparison_data if item['thread_efficiency'] == 0)
        
        print(f"\nThreading Efficiency Analysis:")
        print(f"  High Efficiency (≥80%): {high_efficiency} functions")
        print(f"  Medium Efficiency (50-80%): {medium_efficiency} functions")
        print(f"  Low Efficiency (<50%): {low_efficiency} functions")
        print(f"  No Threading Benefit: {no_threading} functions")


def main():
    """Main function to run the multithreaded comparison visualization"""
    visualizer = EnergyPlusMultithreadedComparisonVisualizer()
    
    if visualizer.load_data():
        if visualizer.prepare_comparison_data():
            # Create chart with baseline bars (default)
            visualizer.create_comparison_chart(show_baseline_bars=True)
            
            # Uncomment the line below to create a version without baseline bars
            # visualizer.create_comparison_chart(show_baseline_bars=False)
        else:
            print("Failed to prepare comparison data")
    else:
        print("Failed to load data files. Please ensure both baseline and multithreaded data files exist.")


if __name__ == "__main__":
    main()