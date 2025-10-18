"""
Simple EnergyPlus performance comparison tool
Usage: python energyplus_simple_compare.py <baseline_file> <measurement_file> [output_file]

Creates a simple bar chart showing performance ratios normalized to baseline.
"""

import argparse
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path


class SimpleEnergyPlusComparator:
    """Simple comparator that only looks at function names and total times"""
    
    def __init__(self, baseline_file, measurement_file, output_file=None):
        self.baseline_file = baseline_file
        self.measurement_file = measurement_file
        self.output_file = output_file or self._generate_output_filename()
        
        self.baseline_data = None
        self.measurement_data = None
        self.comparison_data = None

    def _generate_output_filename(self):
        """Generate output filename from input filenames"""
        baseline_name = Path(self.baseline_file).stem
        measurement_name = Path(self.measurement_file).stem
        return f"{baseline_name}_vs_{measurement_name}_simple.png"

    def load_data(self):
        """Load baseline and measurement JSON files"""
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

        try:
            with open(self.measurement_file, 'r') as f:
                self.measurement_data = json.load(f)
            print(f"✅ Loaded measurement data from {self.measurement_file}")
        except FileNotFoundError:
            print(f"❌ Measurement file '{self.measurement_file}' not found")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in measurement file '{self.measurement_file}'")
            return False
            
        return True

    def prepare_comparison_data(self):
        """Extract function names and times, calculate ratios"""
        if not self.baseline_data or not self.measurement_data:
            print("❌ Data not loaded")
            return False
            
        baseline_functions = self.baseline_data.get('functions', {})
        measurement_functions = self.measurement_data.get('functions', {})
        
        if not baseline_functions or not measurement_functions:
            print("❌ No function data found in input files")
            return False
        
        # Find common functions
        common_functions = set(baseline_functions.keys()) & set(measurement_functions.keys())
        
        if not common_functions:
            print("❌ No common functions found between baseline and measurement data")
            return False
        
        print(f"📊 Found {len(common_functions)} common functions")
        
        # Prepare simple comparison data - just function name, times, and ratio
        comparison_results = []
        
        for func_name in sorted(common_functions):  # Simple alphabetical order
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
        
        self.comparison_data = comparison_results
        print(f"✅ Prepared comparison data for {len(comparison_results)} functions")
        return True

    def create_visualization(self):
        """Create simple bar chart visualization"""
        if not self.comparison_data:
            print("❌ No comparison data available")
            return False
        
        # Extract data for plotting
        functions = [item['function'] for item in self.comparison_data]
        ratios = [item['ratio'] for item in self.comparison_data]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Create bars
        bars = ax.bar(range(len(functions)), ratios)
        
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
        
        # Add horizontal line at y=1.0 (baseline)
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.7, linewidth=1)
        
        # Formatting
        ax.set_xlabel('Functions', fontsize=12, fontweight='bold')
        ax.set_ylabel('Performance Ratio (Normalized to Baseline)', fontsize=12, fontweight='bold')
        ax.set_title('EnergyPlus Performance Comparison\n(Baseline = 1.0)', fontsize=14, fontweight='bold')
        
        # Set x-axis labels
        ax.set_xticks(range(len(functions)))
        ax.set_xticklabels(functions, rotation=45, ha='right', fontsize=8)
        
        # Add grid
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for i, (bar, ratio) in enumerate(zip(bars, ratios)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{ratio:.2f}',
                   ha='center', va='bottom', fontsize=7, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save
        plt.savefig(self.output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Visualization saved as '{self.output_file}'")
        return True

    def print_summary(self):
        """Print simple summary"""
        if not self.comparison_data:
            return
        
        total_baseline = sum(item['baseline_time'] for item in self.comparison_data)
        total_measurement = sum(item['measurement_time'] for item in self.comparison_data)
        overall_ratio = total_measurement / total_baseline if total_baseline > 0 else 1.0
        
        print(f"\n{'='*60}")
        print("SIMPLE PERFORMANCE COMPARISON")
        print('='*60)
        print(f"Baseline File: {self.baseline_file}")
        print(f"Measurement File: {self.measurement_file}")
        print(f"Functions Compared: {len(self.comparison_data)}")
        print(f"Overall Performance Ratio: {overall_ratio:.2f}x")
        
        # Show biggest changes
        print(f"\nBiggest Changes:")
        print("-" * 50)
        sorted_data = sorted(self.comparison_data, key=lambda x: abs(x['ratio'] - 1.0), reverse=True)
        for i, item in enumerate(sorted_data[:10], 1):
            change_icon = "🟢" if item['ratio'] < 0.95 else "🔴" if item['ratio'] > 1.05 else "🟡"
            print(f"{i:2d}. {item['function']:<30} {item['ratio']:>5.2f}x {change_icon}")


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description='Simple EnergyPlus performance comparison visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python energyplus_simple_compare.py baseline.json measurement.json
  python energyplus_simple_compare.py baseline.json measurement.json output.png
        """
    )
    
    parser.add_argument('baseline_file', help='Baseline profiling JSON file')
    parser.add_argument('measurement_file', help='Measurement profiling JSON file')
    parser.add_argument('-o', '--output', help='Output PNG file (auto-generated if not specified)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress summary output')
    
    args = parser.parse_args()
    
    try:
        # Create comparator
        comparator = SimpleEnergyPlusComparator(
            args.baseline_file, 
            args.measurement_file, 
            args.output
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
        
        print(f"\n✅ Successfully created simple comparison: {comparator.output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()