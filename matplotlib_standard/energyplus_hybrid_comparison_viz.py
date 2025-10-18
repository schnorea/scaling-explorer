"""
Comparison visualization script for EnergyPlus baseline vs hybrid profiling data
Creates a single bar chart showing the complex performance effects of 
multithreading improvements offset by memory contention issues
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class EnergyPlusHybridComparisonVisualizer:
    """
    Compares baseline and hybrid EnergyPlus profiling data
    Creates visualization showing net effects of threading + memory contention
    """
    
    def __init__(self, baseline_file="energyplus_profiling_data.json", 
                 hybrid_file="energyplus_profiling_hybrid.json"):
        self.baseline_file = baseline_file
        self.hybrid_file = hybrid_file
        self.baseline_data = None
        self.hybrid_data = None
        self.comparison_data = {}
        
    def load_data(self):
        """Load both baseline and hybrid profiling data"""
        try:
            with open(self.baseline_file, 'r') as f:
                self.baseline_data = json.load(f)
            print(f"Loaded baseline data from {self.baseline_file}")
        except FileNotFoundError:
            print(f"Baseline file {self.baseline_file} not found")
            return False
            
        try:
            with open(self.hybrid_file, 'r') as f:
                self.hybrid_data = json.load(f)
            print(f"Loaded hybrid data from {self.hybrid_file}")
        except FileNotFoundError:
            print(f"Hybrid file {self.hybrid_file} not found")
            return False
            
        return True
    
    def prepare_comparison_data(self):
        """Prepare data for comparison visualization"""
        if not self.baseline_data or not self.hybrid_data:
            return False
            
        baseline_functions = self.baseline_data['functions']
        hybrid_functions = self.hybrid_data['functions']
        
        # Find common functions between both datasets
        common_functions = set(baseline_functions.keys()) & set(hybrid_functions.keys())
        
        comparison_results = []
        
        for func_name in common_functions:
            baseline_time = baseline_functions[func_name]['total_time']
            hybrid_time = hybrid_functions[func_name]['total_time']
            
            # Calculate performance metrics
            if baseline_time > 0:
                performance_ratio = hybrid_time / baseline_time
                net_change_percent = ((hybrid_time - baseline_time) / baseline_time) * 100
            else:
                performance_ratio = 1.0
                net_change_percent = 0.0
            
            # Get hybrid metrics if available
            hybrid_metrics = hybrid_functions[func_name].get('hybrid_metrics', {})
            
            comparison_results.append({
                'function': func_name,
                'baseline_time': baseline_time,
                'hybrid_time': hybrid_time,
                'performance_ratio': performance_ratio,
                'net_change_percent': net_change_percent,
                'net_effect': hybrid_metrics.get('net_effect', 'unknown'),
                'thread_improvement': hybrid_metrics.get('thread_improvement_factor', 1.0),
                'thread_efficiency': hybrid_metrics.get('thread_efficiency', 0.0),
                'contention_factor': hybrid_metrics.get('contention_factor', 1.0),
                'time_saved_threading': hybrid_metrics.get('time_saved_from_threading', 0.0),
                'time_lost_contention': hybrid_metrics.get('time_lost_to_contention', 0.0),
                'baseline_calls': baseline_functions[func_name]['call_count'],
                'hybrid_calls': hybrid_functions[func_name]['call_count']
            })
        
        # Sort by net change (biggest losers first, then gainers)
        comparison_results.sort(key=lambda x: x['net_change_percent'], reverse=True)
        
        self.comparison_data = comparison_results
        return True
    
    def create_comparison_chart(self, show_baseline_bars=True):
        """Create a comprehensive bar chart comparing baseline vs hybrid performance"""
        if not self.comparison_data:
            return
        
        # Set up the figure with a large size for readability
        plt.figure(figsize=(16, 12))
        
        # Extract data for plotting
        function_names = [item['function'] for item in self.comparison_data]
        baseline_normalized = [1.0] * len(function_names)  # All baseline values normalized to 1.0
        hybrid_ratios = [item['performance_ratio'] for item in self.comparison_data]
        net_change_percents = [item['net_change_percent'] for item in self.comparison_data]
        net_effects = [item['net_effect'] for item in self.comparison_data]
        
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
        
        # Color code based on net effect and magnitude
        colors = []
        for ratio, effect in zip(hybrid_ratios, net_effects):
            if effect == 'gain':
                if ratio < 0.7:
                    colors.append('#006400')  # Dark green - excellent gain
                elif ratio < 0.85:
                    colors.append('#228B22')  # Forest green - good gain
                else:
                    colors.append('#90EE90')  # Light green - slight gain
            elif effect == 'mixed':
                if ratio < 1.0:
                    colors.append('#4169E1')  # Royal blue - net positive mixed
                else:
                    colors.append('#8A2BE2')  # Blue violet - net negative mixed
            elif effect in ['loss', 'slight_loss']:
                if ratio > 2.0:
                    colors.append('#8B0000')  # Dark red - severe loss
                elif ratio > 1.5:
                    colors.append('#DC143C')  # Crimson - significant loss
                elif ratio > 1.2:
                    colors.append('#FF6347')  # Tomato - moderate loss
                else:
                    colors.append('#FFA07A')  # Light salmon - slight loss
            elif effect in ['neutral', 'slight_gain']:
                colors.append('#FFD700')  # Gold - neutral/slight change
            else:
                colors.append('#808080')  # Gray - unknown
        
        if show_baseline_bars:
            # Plot baseline bars (all at 1.0, normalized)
            baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4, 
                                  label='Baseline (Normalized)', 
                                  color='#2E8B57', alpha=0.8)
            
            hybrid_bars = ax.bar(x_pos + 0.2, hybrid_ratios, 0.4,
                                label='Hybrid (Threading + Contention)',
                                color=colors, alpha=0.8)
        else:
            # Plot only hybrid bars, centered
            hybrid_bars = ax.bar(x_pos, hybrid_ratios, 0.6,
                                label='Hybrid (Threading + Contention)',
                                color=colors, alpha=0.8)
        
        # Customize the chart
        ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
        ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold')
        
        # Get summary statistics for title
        summary = self.hybrid_data.get('summary', {})
        net_change = summary.get('net_performance_change_percent', 0)
        threading_saved = summary.get('threading_analysis', {}).get('time_saved_from_threading', 0)
        contention_lost = summary.get('threading_analysis', {}).get('time_lost_to_contention', 0)
        
        ax.set_title('EnergyPlus Performance: Baseline vs Multithreading with Memory Contention\n' +
                    f'Net Change: {net_change:+.1f}% | Threading Saved: {threading_saved:.1f}s | Contention Cost: {contention_lost:.1f}s',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Set x-axis labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
        
        # Add horizontal line at y=1.0 for reference (always show for context)
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add value labels on bars for significant changes
        for i, (bar, ratio, net_change, effect) in enumerate(zip(hybrid_bars, hybrid_ratios, net_change_percents, net_effects)):
            if abs(net_change) > 20:  # Only label functions with >20% change
                height = bar.get_height()
                if net_change > 0:  # Performance degradation
                    label_text = f'{ratio:.1f}x\n(+{net_change:.0f}%)'
                    va = 'bottom'
                    y_offset = 0.02
                else:  # Performance improvement
                    label_text = f'{ratio:.1f}x\n({net_change:.0f}%)'
                    va = 'top'
                    y_offset = -0.02
                
                ax.text(bar.get_x() + bar.get_width()/2., height + y_offset,
                       label_text, ha='center', va=va, fontsize=8, fontweight='bold')
        
        # Customize legend
        ax.legend(loc='upper left', fontsize=11)
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set y-axis with appropriate range
        min_ratio = min(hybrid_ratios)
        max_ratio = max(hybrid_ratios)
        ax.set_ylim(max(0, min_ratio * 0.9), max_ratio * 1.1)
        
        # Add color legend for net effects
        from matplotlib.patches import Patch
        effect_legend = [
            Patch(color='#006400', label='Major Net Gain (Threading >> Contention)'),
            Patch(color='#228B22', label='Good Net Gain'),
            Patch(color='#4169E1', label='Mixed Effect (Net Positive)'),
            Patch(color='#8A2BE2', label='Mixed Effect (Net Negative)'),
            Patch(color='#FF6347', label='Moderate Net Loss'),
            Patch(color='#8B0000', label='Major Net Loss (Contention >> Threading)')
        ]
        
        # Add second legend for net effects
        second_legend = ax.legend(handles=effect_legend, loc='upper right', 
                                title='Net Effect Categories', fontsize=10)
        ax.add_artist(second_legend)  # Add back the first legend
        ax.legend(loc='upper left', fontsize=11)
        
        # Add system information as text box
        system_info = (
            f"Hybrid System Configuration:\n"
            f"• CPU Cores: {self.hybrid_data['metadata']['system_conditions']['cpu_cores']}\n"
            f"• Thread Pool: {self.hybrid_data['metadata']['system_conditions']['thread_pool_size']} threads\n"
            f"• Memory Pressure: {self.hybrid_data['metadata']['system_conditions']['memory_pressure']}\n"
            f"• Available Memory: {self.hybrid_data['metadata']['system_conditions']['available_memory']}\n"
            f"• Cache Hit Ratio: {self.hybrid_data['metadata']['system_conditions']['cache_hit_ratio']}\n"
            f"• Threading Efficiency Loss: {self.hybrid_data['metadata']['system_conditions']['threading_efficiency_degradation']}"
        )
        
        ax.text(0.02, 0.02, system_info, transform=ax.transAxes, fontsize=9,
               verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart with appropriate filename
        if show_baseline_bars:
            filename = 'energyplus_baseline_vs_hybrid_comparison.png'
        else:
            filename = 'energyplus_hybrid_only_comparison.png'
            
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        
        print(f"Hybrid comparison chart saved as '{filename}'")
        
        # Display summary statistics
        self.print_comparison_summary()
        
        plt.show()
    
    def print_comparison_summary(self):
        """Print summary statistics of the hybrid comparison"""
        if not self.comparison_data:
            return
        
        print("\n" + "="*90)
        print("HYBRID PERFORMANCE COMPARISON SUMMARY (Threading + Memory Contention)")
        print("="*90)
        
        total_baseline = sum(item['baseline_time'] for item in self.comparison_data)
        total_hybrid = sum(item['hybrid_time'] for item in self.comparison_data)
        overall_change = ((total_hybrid - total_baseline) / total_baseline) * 100
        
        # Get threading analysis from hybrid data
        threading_analysis = self.hybrid_data.get('summary', {}).get('threading_analysis', {})
        
        print(f"Total Baseline Time: {total_baseline:.2f} seconds")
        print(f"Total Hybrid Time: {total_hybrid:.2f} seconds")
        print(f"Net Performance Change: {overall_change:+.1f}%")
        print(f"Time Saved from Threading: {threading_analysis.get('time_saved_from_threading', 0):.2f} seconds")
        print(f"Time Lost to Memory Contention: {threading_analysis.get('time_lost_to_contention', 0):.2f} seconds")
        print(f"Net Time Change: {threading_analysis.get('net_time_change', 0):+.2f} seconds")
        
        # Categorize functions by net effect
        gainers = [item for item in self.comparison_data if item['net_change_percent'] < 0]
        losers = [item for item in self.comparison_data if item['net_change_percent'] > 0]
        neutral = [item for item in self.comparison_data if abs(item['net_change_percent']) < 5]
        
        print(f"\nTop 10 Biggest Changes:")
        print("-" * 85)
        for i, item in enumerate(self.comparison_data[:10], 1):
            effect_icon = "🟢" if item['net_change_percent'] < -10 else "🔴" if item['net_change_percent'] > 10 else "🟡"
            print(f"{i:2d}. {item['function']:<35} "
                  f"{item['performance_ratio']:>5.1f}x ({item['net_change_percent']:+6.1f}%) "
                  f"{effect_icon} [{item['net_effect']}]")
        
        # Threading efficiency analysis
        print(f"\nThreading Efficiency Analysis:")
        print("-" * 40)
        high_efficiency = sum(1 for item in self.comparison_data if item['thread_efficiency'] >= 0.6)
        medium_efficiency = sum(1 for item in self.comparison_data if 0.3 <= item['thread_efficiency'] < 0.6)
        low_efficiency = sum(1 for item in self.comparison_data if 0 < item['thread_efficiency'] < 0.3)
        no_threading = sum(1 for item in self.comparison_data if item['thread_efficiency'] == 0)
        
        print(f"  High Threading Efficiency (≥60%): {high_efficiency} functions")
        print(f"  Medium Threading Efficiency (30-60%): {medium_efficiency} functions")
        print(f"  Low Threading Efficiency (<30%): {low_efficiency} functions")
        print(f"  No Threading Benefit: {no_threading} functions")
        
        # Net effect distribution
        print(f"\nNet Effect Distribution:")
        print("-" * 25)
        effect_counts = {}
        for item in self.comparison_data:
            effect = item['net_effect']
            effect_counts[effect] = effect_counts.get(effect, 0) + 1
        
        for effect, count in sorted(effect_counts.items()):
            print(f"  {effect.title()}: {count} functions")
        
        print(f"\nOverall Assessment:")
        print("-" * 20)
        if overall_change < -10:
            print("🟢 Threading optimizations successfully overcome memory contention")
        elif overall_change > 10:
            print("🔴 Memory contention significantly outweighs threading benefits")
        else:
            print("🟡 Mixed results - threading and contention effects roughly balanced")


def main():
    """Main function to run the hybrid comparison visualization"""
    visualizer = EnergyPlusHybridComparisonVisualizer()
    
    if visualizer.load_data():
        if visualizer.prepare_comparison_data():
            # Create chart with baseline bars (default)
            visualizer.create_comparison_chart(show_baseline_bars=True)
            
            # Uncomment the line below to create a version without baseline bars
            # visualizer.create_comparison_chart(show_baseline_bars=False)
        else:
            print("Failed to prepare comparison data")
    else:
        print("Failed to load data files. Please ensure both baseline and hybrid data files exist.")


if __name__ == "__main__":
    main()