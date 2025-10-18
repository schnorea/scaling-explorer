"""
Multi-chart EnergyPlus performance comparison tool
Usage: python energyplus_multi_compare.py <baseline_file> <measurement_file1> [measurement_file2] ... [options]

Creates multiple aligned charts for easy comparison of different scenarios.
"""

import argparse
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

# Try to use interactive backend, fall back to Agg if not available
try:
    matplotlib.use('TkAgg')
except ImportError:
    try:
        matplotlib.use('Qt5Agg')
    except ImportError:
        matplotlib.use('Agg')
        print("⚠️  No interactive backend available, using static mode only")


class MultiChartComparator:
    """Compare multiple measurement files against a single baseline"""
    
    def __init__(self, baseline_file, measurement_files, output_file=None, interactive=True, deviation_bars=False):
        self.baseline_file = baseline_file
        self.measurement_files = measurement_files
        self.output_file = output_file or self._generate_output_filename()
        self.interactive = interactive
        self.deviation_bars = deviation_bars
        
        self.baseline_data = None
        self.measurement_data_list = []
        self.comparison_data_list = []
        self.common_functions = []

    def _generate_output_filename(self):
        """Generate output filename from input filenames"""
        baseline_name = Path(self.baseline_file).stem
        return f"{baseline_name}_multi_comparison.png"

    def load_data(self):
        """Load baseline and all measurement JSON files"""
        # Load baseline
        try:
            with open(self.baseline_file, 'r') as f:
                self.baseline_data = json.load(f)
            print(f"✅ Loaded baseline data from {self.baseline_file}")
        except FileNotFoundError:
            print(f"❌ Baseline file '{self.baseline_file}' not found")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in baseline file '{self.baseline_file}'")
            return False

        # Load all measurement files
        self.measurement_data_list = []
        for measurement_file in self.measurement_files:
            try:
                with open(measurement_file, 'r') as f:
                    measurement_data = json.load(f)
                self.measurement_data_list.append({
                    'data': measurement_data,
                    'filename': measurement_file,
                    'name': Path(measurement_file).stem
                })
                print(f"✅ Loaded measurement data from {measurement_file}")
            except FileNotFoundError:
                print(f"❌ Measurement file '{measurement_file}' not found")
                return False
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in measurement file '{measurement_file}'")
                return False
        
        return True

    def prepare_comparison_data(self):
        """Find common functions and prepare comparison data for all measurements"""
        if not self.baseline_data or not self.measurement_data_list:
            print("❌ Data not loaded")
            return False
            
        baseline_functions = self.baseline_data.get('functions', {})
        if not baseline_functions:
            print("❌ No function data found in baseline file")
            return False
        
        # Find functions common to ALL files
        common_functions = set(baseline_functions.keys())
        for measurement_info in self.measurement_data_list:
            measurement_functions = measurement_info['data'].get('functions', {})
            if not measurement_functions:
                print(f"❌ No function data found in {measurement_info['filename']}")
                return False
            common_functions = common_functions & set(measurement_functions.keys())
        
        if not common_functions:
            print("❌ No common functions found across all files")
            return False
        
        self.common_functions = sorted(common_functions)  # Alphabetical order
        print(f"📊 Found {len(self.common_functions)} common functions across all files")
        
        # Prepare comparison data for each measurement
        self.comparison_data_list = []
        for measurement_info in self.measurement_data_list:
            measurement_functions = measurement_info['data'].get('functions', {})
            
            comparison_results = []
            for func_name in self.common_functions:
                baseline_time = baseline_functions[func_name]['total_time']
                measurement_time = measurement_functions[func_name]['total_time']
                
                # Calculate ratio (normalized to baseline)
                if baseline_time > 0:
                    ratio = measurement_time / baseline_time
                else:
                    ratio = 1.0
                
                comparison_results.append({
                    'function': func_name,
                    'baseline_time': baseline_time,
                    'measurement_time': measurement_time,
                    'ratio': ratio
                })
            
            self.comparison_data_list.append({
                'data': comparison_results,
                'name': measurement_info['name'],
                'filename': measurement_info['filename']
            })
        
        print(f"✅ Prepared comparison data for {len(self.comparison_data_list)} measurements")
        return True

    def create_visualization(self):
        """Create multi-chart visualization with aligned subplots"""
        if not self.comparison_data_list:
            print("❌ No comparison data available")
            return False
        
        num_charts = len(self.comparison_data_list)
        if num_charts > 16:
            print(f"⚠️  Too many charts ({num_charts}), limiting to first 16")
            self.comparison_data_list = self.comparison_data_list[:16]
            num_charts = 16
        
        # Calculate grid layout - prefer vertical stacking with some horizontal spread
        if num_charts <= 4:
            cols = 1
            rows = num_charts
        elif num_charts <= 8:
            cols = 2
            rows = (num_charts + 1) // 2
        elif num_charts <= 12:
            cols = 3
            rows = (num_charts + 2) // 3
        else:
            cols = 4
            rows = (num_charts + 3) // 4
        
        # Calculate global Y-axis limits across all charts for consistency
        all_ratios = []
        for comparison_info in self.comparison_data_list:
            comparison_data = comparison_info['data']
            ratios = [item['ratio'] for item in comparison_data]
            all_ratios.extend(ratios)
        
        if self.deviation_bars:
            # For deviation bars, we need to show deviations from 1.0
            max_deviation_up = max(max(all_ratios) - 1.0, 0.2)  # At least 0.2 above baseline
            max_deviation_down = max(1.0 - min(all_ratios), 0.2)  # At least 0.2 below baseline
            y_padding = 0.1
            y_min = 1.0 - max_deviation_down * (1 + y_padding)
            y_max = 1.0 + max_deviation_up * (1 + y_padding)
        else:
            # Traditional bars from zero
            global_max_ratio = max(max(all_ratios), 1.2)  # At least 1.2 to show baseline clearly
            global_min_ratio = min(min(all_ratios), 0.8)  # At least 0.8 to show baseline clearly
            y_padding = 0.1
            y_min = global_min_ratio * (1 - y_padding)
            y_max = global_max_ratio * (1 + y_padding)
        
        # Create figure with subplots
        fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 4*rows))
        if rows == 1 and cols == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        # Create each chart
        for i, comparison_info in enumerate(self.comparison_data_list):
            ax = axes[i]
            # Only show labels on bottom row and left column
            show_ylabel = (i % cols == 0)  # Left column
            show_xlabel = (i >= num_charts - cols) or (i == num_charts - 1)  # Bottom row or last chart
            self._create_single_chart(ax, comparison_info, show_ylabel, show_xlabel, y_min, y_max)
        
        # Hide unused subplots
        for i in range(num_charts, len(axes)):
            axes[i].set_visible(False)
        
        # Add overall title
        title_suffix = "Deviation Bars" if self.deviation_bars else "Same Scale"
        fig.suptitle(f'EnergyPlus Performance Comparison - Multiple Scenarios\n(Baseline = 1.0, {title_suffix})', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.93, hspace=0.15, wspace=0.2)
        
        # Save PNG version
        plt.savefig(self.output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved as '{self.output_file}'")
        
        # Show interactive version if requested
        if self.interactive:
            try:
                print("🖱️  Showing interactive multi-chart view!")
                print("   Close the window when done viewing.")
                plt.show()
            except Exception as e:
                print(f"⚠️  Interactive display failed: {e}")
                print("   Static PNG file created successfully.")
        else:
            plt.close()
        
        return True

    def _create_single_chart(self, ax, comparison_info, show_ylabel=True, show_xlabel=True, y_min=None, y_max=None):
        """Create a single chart in the given axes"""
        comparison_data = comparison_info['data']
        chart_name = comparison_info['name']
        
        # Extract data for plotting
        ratios = [item['ratio'] for item in comparison_data]
        
        if self.deviation_bars:
            # Create deviation bars that start from baseline (1.0)
            x_positions = range(len(self.common_functions))
            
            # Create bars showing deviations from baseline
            for i, ratio in enumerate(ratios):
                if ratio >= 1.0:
                    # Slowdown: red bar going up from baseline
                    height = ratio - 1.0
                    bottom = 1.0
                    color = '#DC143C' if ratio > 1.05 else '#708090'
                else:
                    # Speedup: green bar going down from baseline
                    height = 1.0 - ratio
                    bottom = ratio
                    color = '#2E8B57' if ratio < 0.95 else '#708090'
                
                ax.bar(i, height, bottom=bottom, width=0.8, color=color, alpha=0.8)
            
            # Create invisible bars for consistent spacing (helps with hover if we add it later)
            bars = ax.bar(x_positions, [0] * len(ratios), width=0.8, alpha=0)
        else:
            # Traditional bars from zero
            bars = ax.bar(range(len(self.common_functions)), ratios, width=0.8)
            
            # Color bars: green for improvement (<1.0), red for degradation (>1.0), gray for no change
            colors = []
            for ratio in ratios:
                if ratio < 0.95:  # More than 5% improvement
                    colors.append('#2E8B57')  # Sea green
                elif ratio > 1.05:  # More than 5% degradation
                    colors.append('#DC143C')  # Crimson
                else:
                    colors.append('#708090')  # Slate gray
            
            for bar, color in zip(bars, colors):
                bar.set_color(color)
        
        # Add horizontal line at y=1.0 (baseline) - this will now be in the same position across all charts
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.7, linewidth=2)
        
        # Formatting
        ax.set_title(chart_name, fontsize=12, fontweight='bold', pad=10)
        
        # Only show Y-axis label on leftmost charts
        if show_ylabel:
            ylabel = 'Performance Deviation' if self.deviation_bars else 'Performance Ratio'
            ax.set_ylabel(ylabel, fontsize=10, fontweight='bold')
        
        # Only show X-axis labels on bottom charts
        if show_xlabel:
            ax.set_xticks(range(len(self.common_functions)))
            ax.set_xticklabels(self.common_functions, rotation=45, ha='right', fontsize=6)
        else:
            # Still set ticks but hide labels
            ax.set_xticks(range(len(self.common_functions)))
            ax.set_xticklabels([])
        
        # Add grid
        ax.grid(True, alpha=0.3, axis='y')
        
        # Set consistent y-axis limits across all charts
        if y_min is not None and y_max is not None:
            ax.set_ylim(y_min, y_max)
        
        # Add summary statistics as text
        total_baseline = sum(item['baseline_time'] for item in comparison_data)
        total_measurement = sum(item['measurement_time'] for item in comparison_data)
        overall_ratio = total_measurement / total_baseline if total_baseline > 0 else 1.0
        
        # Add overall performance text
        perf_text = f"Overall: {overall_ratio:.2f}x"
        perf_color = '#2E8B57' if overall_ratio < 0.95 else '#DC143C' if overall_ratio > 1.05 else '#708090'
        ax.text(0.02, 0.98, perf_text, transform=ax.transAxes, fontsize=10, fontweight='bold',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor=perf_color, alpha=0.3))

    def print_summary(self):
        """Print summary for all comparisons"""
        if not self.comparison_data_list:
            return
        
        print(f"\n{'='*80}")
        print("MULTI-CHART PERFORMANCE COMPARISON SUMMARY")
        print('='*80)
        print(f"Baseline File: {self.baseline_file}")
        print(f"Number of Comparisons: {len(self.comparison_data_list)}")
        print(f"Functions Compared: {len(self.common_functions)}")
        
        print(f"\nOverall Performance Ratios:")
        print("-" * 50)
        
        for i, comparison_info in enumerate(self.comparison_data_list, 1):
            comparison_data = comparison_info['data']
            total_baseline = sum(item['baseline_time'] for item in comparison_data)
            total_measurement = sum(item['measurement_time'] for item in comparison_data)
            overall_ratio = total_measurement / total_baseline if total_baseline > 0 else 1.0
            
            change_icon = "🟢" if overall_ratio < 0.95 else "🔴" if overall_ratio > 1.05 else "🟡"
            print(f"{i:2d}. {comparison_info['name']:<40} {overall_ratio:>5.2f}x {change_icon}")


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description='Multi-chart EnergyPlus performance comparison visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python energyplus_multi_compare.py baseline.json contended.json multithreaded.json
  python energyplus_multi_compare.py baseline.json *.json -o comparison.png
  python energyplus_multi_compare.py baseline.json file1.json file2.json --deviation-bars
  python energyplus_multi_compare.py baseline.json file1.json file2.json file3.json --no-interactive
        """
    )
    
    parser.add_argument('baseline_file', help='Baseline profiling JSON file')
    parser.add_argument('measurement_files', nargs='+', help='One or more measurement profiling JSON files')
    parser.add_argument('-o', '--output', help='Output PNG file (auto-generated if not specified)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress summary output')
    parser.add_argument('--no-interactive', action='store_true', help='Skip interactive display, only create PNG')
    parser.add_argument('--deviation-bars', action='store_true', help='Show bars as deviations from baseline (1.0) instead of from zero')
    
    args = parser.parse_args()
    
    try:
        # Create comparator
        comparator = MultiChartComparator(
            args.baseline_file, 
            args.measurement_files, 
            args.output,
            interactive=not args.no_interactive,
            deviation_bars=args.deviation_bars
        )
        
        # Load data
        if not comparator.load_data():
            sys.exit(1)
        
        # Prepare comparison
        if not comparator.prepare_comparison_data():
            sys.exit(1)
        
        # Create visualization
        if not comparator.create_visualization():
            sys.exit(1)
        
        # Print summary
        if not args.quiet:
            comparator.print_summary()
        
        print(f"\n✅ Successfully created multi-chart comparison: {comparator.output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()