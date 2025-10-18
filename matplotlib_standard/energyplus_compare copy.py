"""
Command-line EnergyPlus performance comparison visualization tool
Usage: python energyplus_compare.py <baseline_file> <measurement_file> [options]

Creates bar chart visualizations comparing baseline performance with measurement data.
Functions are always displayed in the same consistent order for easy comparison.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

class EnergyPlusCommandLineComparator:
    """
    Command-line tool for comparing EnergyPlus profiling data
    Derives and maintains consistent function ordering from data files
    """
    
    def __init__(self, baseline_file, measurement_file, output_file=None, show_baseline=True, ordering_file="function_order.json"):
        self.baseline_file = baseline_file
        self.measurement_file = measurement_file
        self.output_file = output_file or self._generate_output_filename()
        self.show_baseline = show_baseline
        self.ordering_file = ordering_file
        self.baseline_data = None
        self.measurement_data = None
        self.comparison_data = []
        self.function_order = []
        
    def _generate_output_filename(self):
        """Generate output filename based on input files"""
        baseline_name = Path(self.baseline_file).stem
        measurement_name = Path(self.measurement_file).stem
        return f"{baseline_name}_vs_{measurement_name}_comparison.png"
    
    def load_data(self):
        """Load both baseline and measurement profiling data"""
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
        """Prepare data for comparison visualization with consistent ordering"""
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
        
        # Load or create function ordering
        self._load_or_create_function_order(common_functions)
        
        # Prepare comparison data
        comparison_results = []
        
        for func_name in self.function_order:
            baseline_time = baseline_functions[func_name]['total_time']
            measurement_time = measurement_functions[func_name]['total_time']
            
            # Calculate performance metrics
            if baseline_time > 0:
                performance_ratio = measurement_time / baseline_time
                change_percent = ((measurement_time - baseline_time) / baseline_time) * 100
            else:
                performance_ratio = 1.0
                change_percent = 0.0
            
            # Detect measurement type and get additional metrics
            measurement_type = self._detect_measurement_type()
            additional_metrics = self._extract_additional_metrics(func_name, measurement_functions)
            
            comparison_results.append({
                'function': func_name,
                'baseline_time': baseline_time,
                'measurement_time': measurement_time,
                'performance_ratio': performance_ratio,
                'change_percent': change_percent,
                'baseline_calls': baseline_functions[func_name]['call_count'],
                'measurement_calls': measurement_functions[func_name]['call_count'],
                'measurement_type': measurement_type,
                **additional_metrics
            })
        
        self.comparison_data = comparison_results
        print(f"✅ Prepared comparison data for {len(comparison_results)} functions")
        return True
    
    def _detect_measurement_type(self):
        """Detect the type of measurement (contention, threading, hybrid, etc.)"""
        metadata = self.measurement_data.get('metadata', {})
        system_conditions = metadata.get('system_conditions', {})
        
        if 'scenario' in system_conditions:
            return system_conditions['scenario']
        elif 'memory_pressure' in system_conditions and 'thread_pool_size' in system_conditions:
            return 'hybrid'
        elif 'memory_pressure' in system_conditions:
            return 'contention'
        elif 'thread_pool_size' in system_conditions or 'cpu_cores' in system_conditions:
            return 'threading'
        else:
            return 'unknown'
    
    def _extract_additional_metrics(self, func_name, measurement_functions):
        """Extract additional metrics based on measurement type"""
        func_data = measurement_functions[func_name]
        additional = {}
        
        # Check for threading metrics
        if 'threading_metrics' in func_data:
            tm = func_data['threading_metrics']
            additional.update({
                'thread_improvement': tm.get('improvement_factor', 1.0),
                'thread_efficiency': tm.get('thread_efficiency', 0.0),
                'time_saved_threading': tm.get('time_saved', 0.0)
            })
        
        # Check for contention metrics
        if 'contention_metrics' in func_data:
            cm = func_data['contention_metrics']
            additional.update({
                'contention_factor': cm.get('contention_factor', 1.0),
                'performance_degradation': cm.get('performance_degradation_percent', 0.0)
            })
        
        # Check for hybrid metrics
        if 'hybrid_metrics' in func_data:
            hm = func_data['hybrid_metrics']
            additional.update({
                'net_effect': hm.get('net_effect', 'unknown'),
                'thread_improvement': hm.get('thread_improvement_factor', 1.0),
                'thread_efficiency': hm.get('thread_efficiency', 0.0),
                'contention_factor': hm.get('contention_factor', 1.0),
                'time_saved_threading': hm.get('time_saved_from_threading', 0.0),
                'time_lost_contention': hm.get('time_lost_to_contention', 0.0)
            })
        
        return additional
    
    def create_visualization(self):
        """Create the bar chart visualization"""
        if not self.comparison_data:
            print("❌ No comparison data available")
            return False
        
        # Set up the plot
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(20, 12))
        
        # Extract data for plotting
        function_names = [item['function'] for item in self.comparison_data]
        baseline_normalized = [1.0] * len(function_names)
        measurement_ratios = [item['performance_ratio'] for item in self.comparison_data]
        change_percents = [item['change_percent'] for item in self.comparison_data]
        measurement_type = self.comparison_data[0]['measurement_type']
        
        # Shorten function names for readability
        short_names = []
        for name in function_names:
            if len(name) > 20:
                short_name = name.replace('Calc', '').replace('Simulate', 'Sim').replace('Manager', 'Mgr')
                if len(short_name) > 20:
                    short_name = short_name[:17] + '...'
                short_names.append(short_name)
            else:
                short_names.append(name)
        
        # Create x positions
        x_pos = np.arange(len(function_names))
        
        # Color code based on measurement type and performance change
        colors = self._get_colors_by_type(measurement_ratios, change_percents, measurement_type)
        
        # Plot bars
        if self.show_baseline:
            baseline_bars = ax.bar(x_pos - 0.2, baseline_normalized, 0.4,
                                  label='Baseline (Normalized)', color='#2E8B57', alpha=0.8)
            measurement_bars = ax.bar(x_pos + 0.2, measurement_ratios, 0.4,
                                     label=f'Measurement ({measurement_type.title()})',
                                     color=colors, alpha=0.8)
        else:
            measurement_bars = ax.bar(x_pos, measurement_ratios, 0.6,
                                     label=f'Measurement ({measurement_type.title()})',
                                     color=colors, alpha=0.8)
        
        # Customize the chart
        ax.set_xlabel('Functions (Canonical Order)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Performance Ratio (Baseline = 1.0)', fontsize=12, fontweight='bold')
        
        # Create informative title
        title = self._generate_title(measurement_type)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Set x-axis
        ax.set_xticks(x_pos)
        ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
        
        # Add reference line
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add value labels for significant changes
        self._add_value_labels(ax, measurement_bars, measurement_ratios, change_percents)
        
        # Customize appearance
        ax.legend(loc='upper left', fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Set appropriate y-axis range
        min_ratio = min(measurement_ratios)
        max_ratio = max(measurement_ratios)
        ax.set_ylim(max(0, min_ratio * 0.9), max_ratio * 1.1)
        
        # Add system information
        self._add_system_info(ax)
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(self.output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Visualization saved as '{self.output_file}'")
        return True
    
    def _get_colors_by_type(self, ratios, changes, measurement_type):
        """Get appropriate colors based on measurement type and performance"""
        colors = []
        
        for ratio, change in zip(ratios, changes):
            if measurement_type in ['threading', 'multithreaded']:
                # For threading: lower ratios are better (improvements)
                if ratio < 0.7:
                    colors.append('#006400')  # Dark green - excellent
                elif ratio < 0.85:
                    colors.append('#228B22')  # Good green
                elif ratio < 1.0:
                    colors.append('#90EE90')  # Light green - slight improvement
                elif ratio < 1.1:
                    colors.append('#FFD700')  # Gold - minimal change
                else:
                    colors.append('#FFA07A')  # Light red - slight loss
            
            elif measurement_type in ['contention', 'memory_contention']:
                # For contention: higher ratios are worse (degradation)
                if ratio < 1.2:
                    colors.append('#90EE90')  # Light green - minimal impact
                elif ratio < 1.8:
                    colors.append('#FFA500')  # Orange - moderate impact
                elif ratio < 2.5:
                    colors.append('#FF4500')  # Red-orange - significant impact
                else:
                    colors.append('#8B0000')  # Dark red - severe impact
            
            elif measurement_type == 'hybrid':
                # For hybrid: complex coloring based on net effect
                if hasattr(self, 'comparison_data'):
                    net_effect = next((item.get('net_effect', 'unknown') 
                                     for item in self.comparison_data 
                                     if item['performance_ratio'] == ratio), 'unknown')
                    
                    if net_effect == 'gain':
                        colors.append('#228B22')  # Forest green
                    elif net_effect == 'mixed':
                        colors.append('#4169E1' if ratio < 1.0 else '#8A2BE2')  # Blue variants
                    elif net_effect in ['loss', 'slight_loss']:
                        colors.append('#DC143C' if ratio > 1.5 else '#FF6347')  # Red variants
                    else:
                        colors.append('#FFD700')  # Gold - neutral/unknown
                else:
                    colors.append('#808080')  # Gray - unknown
            
            else:
                # Default coloring for unknown types
                if change < -10:
                    colors.append('#228B22')  # Green - improvement
                elif change > 10:
                    colors.append('#DC143C')  # Red - degradation
                else:
                    colors.append('#FFD700')  # Gold - neutral
        
        return colors
    
    def _generate_title(self, measurement_type):
        """Generate an appropriate title based on measurement type"""
        baseline_name = Path(self.baseline_file).stem
        measurement_name = Path(self.measurement_file).stem
        
        type_descriptions = {
            'threading': 'Multithreading Optimization',
            'multithreaded': 'Multithreading Optimization',
            'contention': 'Memory Contention Impact',
            'memory_contention': 'Memory Contention Impact',
            'hybrid': 'Multithreading with Memory Contention',
            'Multithreaded with Memory Contention': 'Multithreading with Memory Contention'
        }
        
        description = type_descriptions.get(measurement_type, 'Performance Comparison')
        
        return f'EnergyPlus Performance Analysis: {description}\n{baseline_name} vs {measurement_name}'
    
    def _add_value_labels(self, ax, bars, ratios, changes):
        """Add value labels to bars for significant changes"""
        for bar, ratio, change in zip(bars, ratios, changes):
            if abs(change) > 15:  # Only label significant changes
                height = bar.get_height()
                
                if change > 0:  # Performance degradation
                    label_text = f'{ratio:.1f}x'
                    va = 'bottom'
                    y_offset = 0.02
                else:  # Performance improvement
                    label_text = f'{ratio:.1f}x'
                    va = 'top' if height < 0.8 else 'bottom'
                    y_offset = -0.02 if height < 0.8 else 0.02
                
                ax.text(bar.get_x() + bar.get_width()/2., height + y_offset,
                       label_text, ha='center', va=va, fontsize=8, fontweight='bold')
    
    def _add_system_info(self, ax):
        """Add system information text box"""
        metadata = self.measurement_data.get('metadata', {})
        system_conditions = metadata.get('system_conditions', {})
        
        info_lines = []
        
        # Add relevant system information based on what's available
        if 'cpu_cores' in system_conditions:
            info_lines.append(f"CPU Cores: {system_conditions['cpu_cores']}")
        if 'thread_pool_size' in system_conditions:
            info_lines.append(f"Thread Pool: {system_conditions['thread_pool_size']}")
        if 'memory_pressure' in system_conditions:
            info_lines.append(f"Memory Pressure: {system_conditions['memory_pressure']}")
        if 'available_memory' in system_conditions:
            info_lines.append(f"Available Memory: {system_conditions['available_memory']}")
        if 'cache_hit_ratio' in system_conditions:
            info_lines.append(f"Cache Hit Ratio: {system_conditions['cache_hit_ratio']}")
        
        if info_lines:
            system_info = "System Configuration:\n" + "\n".join(f"• {line}" for line in info_lines)
            ax.text(0.02, 0.98, system_info, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.comparison_data:
            return
        
        total_baseline = sum(item['baseline_time'] for item in self.comparison_data)
        total_measurement = sum(item['measurement_time'] for item in self.comparison_data)
        overall_change = ((total_measurement - total_baseline) / total_baseline) * 100
        
        print(f"\n{'='*80}")
        print("PERFORMANCE COMPARISON SUMMARY")
        print('='*80)
        print(f"Baseline File: {self.baseline_file}")
        print(f"Measurement File: {self.measurement_file}")
        print(f"Measurement Type: {self.comparison_data[0]['measurement_type'].title()}")
        print(f"Functions Compared: {len(self.comparison_data)}")
        print(f"Total Baseline Time: {total_baseline:.2f} seconds")
        print(f"Total Measurement Time: {total_measurement:.2f} seconds")
        print(f"Overall Performance Change: {overall_change:+.1f}%")
        
        # Show top changes
        print(f"\nTop 10 Biggest Changes:")
        print("-" * 70)
        sorted_data = sorted(self.comparison_data, key=lambda x: abs(x['change_percent']), reverse=True)
        for i, item in enumerate(sorted_data[:10], 1):
            change_icon = "🟢" if item['change_percent'] < -5 else "🔴" if item['change_percent'] > 5 else "🟡"
            print(f"{i:2d}. {item['function']:<30} {item['performance_ratio']:>5.1f}x ({item['change_percent']:+6.1f}%) {change_icon}")

    def _load_or_create_function_order(self, common_functions):
        """Load existing function order or create new one from data"""
        if Path(self.ordering_file).exists():
            try:
                with open(self.ordering_file, 'r') as f:
                    order_data = json.load(f)
                
                stored_order = order_data.get('function_order', [])
                
                # Check if stored order covers all common functions
                if set(stored_order) >= common_functions:
                    # Use stored order, filtering to only include common functions
                    self.function_order = [func for func in stored_order if func in common_functions]
                    print(f"📋 Using existing function order from {self.ordering_file}")
                    print(f"🔄 Order covers {len(self.function_order)} functions")
                    return True
                else:
                    print(f"⚠️ Existing order file doesn't cover all functions, creating new order")
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️ Error reading order file: {e}, creating new order")
        
        # Create new function order based on data analysis
        self.function_order = self._derive_function_order(common_functions)
        self._save_function_order()
        return True
    
    def _derive_function_order(self, common_functions):
        """Derive logical function order from profiling data characteristics"""
        baseline_functions = self.baseline_data.get('functions', {})
        
        # Categorize functions by characteristics
        categorized_functions = {
            'initialization': [],
            'weather_solar': [],
            'zone_surface': [],
            'heat_balance': [],
            'hvac_systems': [],
            'plant_systems': [],
            'math_utilities': [],
            'psychrometric': [],
            'economics': [],
            'output_reporting': [],
            'other': []
        }
        
        for func_name in common_functions:
            func_data = baseline_functions.get(func_name, {})
            call_count = func_data.get('call_count', 0)
            
            # Categorize based on function name patterns and call frequency
            if any(pattern in func_name for pattern in ['GetInput', 'Initialize', 'Setup', 'Validate']):
                categorized_functions['initialization'].append(func_name)
            elif any(pattern in func_name for pattern in ['Weather', 'Solar', 'Sun']):
                categorized_functions['weather_solar'].append(func_name)
            elif any(pattern in func_name for pattern in ['Zone', 'Surface', 'Window', 'Interior', 'Exterior', 'HeatGain']):
                categorized_functions['zone_surface'].append(func_name)
            elif any(pattern in func_name for pattern in ['HeatBal', 'FiniteDiff', 'TransferFunction']):
                categorized_functions['heat_balance'].append(func_name)
            elif any(pattern in func_name for pattern in ['HVAC', 'AirLoop', 'Fan', 'Coil', 'Chiller', 'Boiler', 'Pump']):
                categorized_functions['hvac_systems'].append(func_name)
            elif any(pattern in func_name for pattern in ['Plant', 'Loop', 'Valve']):
                categorized_functions['plant_systems'].append(func_name)
            elif call_count > 10000 and any(pattern in func_name for pattern in ['POLYF', 'Curve', 'Table', 'Regular', 'Interpolate']):
                categorized_functions['math_utilities'].append(func_name)
            elif func_name.startswith('Psy'):
                categorized_functions['psychrometric'].append(func_name)
            elif any(pattern in func_name for pattern in ['Tariff', 'Bill', 'Economic']):
                categorized_functions['economics'].append(func_name)
            elif any(pattern in func_name for pattern in ['Report', 'Update', 'Write', 'Output']):
                categorized_functions['output_reporting'].append(func_name)
            else:
                categorized_functions['other'].append(func_name)
        
        # Sort within each category
        for category in categorized_functions:
            if category == 'initialization':
                # Sort initialization by likely execution order
                init_order = ['GetInput', 'Initialize', 'Setup', 'Validate']
                categorized_functions[category].sort(key=lambda x: next((i for i, pattern in enumerate(init_order) if pattern in x), 999))
            elif category in ['math_utilities', 'psychrometric']:
                # Sort high-frequency functions by call count (descending)
                categorized_functions[category].sort(key=lambda x: baseline_functions.get(x, {}).get('call_count', 0), reverse=True)
            else:
                # Sort alphabetically for other categories
                categorized_functions[category].sort()
        
        # Combine categories in logical execution order
        ordered_functions = []
        category_order = [
            'initialization',
            'weather_solar',
            'zone_surface', 
            'heat_balance',
            'hvac_systems',
            'plant_systems',
            'math_utilities',
            'psychrometric',
            'economics',
            'output_reporting',
            'other'
        ]
        
        for category in category_order:
            ordered_functions.extend(categorized_functions[category])
        
        print(f"📊 Derived function order with {len(ordered_functions)} functions:")
        for category in category_order:
            if categorized_functions[category]:
                print(f"  • {category.replace('_', ' ').title()}: {len(categorized_functions[category])} functions")
        
        return ordered_functions
    
    def _save_function_order(self):
        """Save the derived function order to JSON file"""
        order_data = {
            'metadata': {
                'created_from_baseline': self.baseline_file,
                'created_from_measurement': self.measurement_file,
                'creation_timestamp': datetime.now().isoformat(),
                'total_functions': len(self.function_order),
                'description': 'Function ordering derived from profiling data characteristics'
            },
            'function_order': self.function_order,
            'categories': self._get_function_categories()
        }
        
        try:
            with open(self.ordering_file, 'w') as f:
                json.dump(order_data, f, indent=2)
            print(f"💾 Saved function order to {self.ordering_file}")
        except Exception as e:
            print(f"⚠️ Warning: Could not save function order: {e}")
    
    def _get_function_categories(self):
        """Get categorization information for the ordering file"""
        baseline_functions = self.baseline_data.get('functions', {})
        categories = {}
        
        for func_name in self.function_order:
            func_data = baseline_functions.get(func_name, {})
            call_count = func_data.get('call_count', 0)
            total_time = func_data.get('total_time', 0)
            
            # Determine category
            if any(pattern in func_name for pattern in ['GetInput', 'Initialize', 'Setup', 'Validate']):
                category = 'initialization'
            elif any(pattern in func_name for pattern in ['Weather', 'Solar', 'Sun']):
                category = 'weather_solar'
            elif any(pattern in func_name for pattern in ['Zone', 'Surface', 'Window', 'Interior', 'Exterior', 'HeatGain']):
                category = 'zone_surface'
            elif any(pattern in func_name for pattern in ['HeatBal', 'FiniteDiff', 'TransferFunction']):
                category = 'heat_balance'
            elif any(pattern in func_name for pattern in ['HVAC', 'AirLoop', 'Fan', 'Coil', 'Chiller', 'Boiler', 'Pump']):
                category = 'hvac_systems'
            elif any(pattern in func_name for pattern in ['Plant', 'Loop', 'Valve']):
                category = 'plant_systems'
            elif call_count > 10000 and any(pattern in func_name for pattern in ['POLYF', 'Curve', 'Table', 'Regular', 'Interpolate']):
                category = 'math_utilities'
            elif func_name.startswith('Psy'):
                category = 'psychrometric'
            elif any(pattern in func_name for pattern in ['Tariff', 'Bill', 'Economic']):
                category = 'economics'
            elif any(pattern in func_name for pattern in ['Report', 'Update', 'Write', 'Output']):
                category = 'output_reporting'
            else:
                category = 'other'
            
            categories[func_name] = {
                'category': category,
                'call_count': call_count,
                'total_time': total_time
            }
        
        return categories


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description='Create performance comparison visualizations for EnergyPlus profiling data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python energyplus_compare.py baseline.json contended.json
  python energyplus_compare.py baseline.json threaded.json --no-baseline
  python energyplus_compare.py baseline.json hybrid.json --output custom_chart.png
        """
    )
    
    parser.add_argument('baseline_file', help='Path to baseline profiling JSON file')
    parser.add_argument('measurement_file', help='Path to measurement profiling JSON file')
    parser.add_argument('--output', '-o', help='Output PNG filename (auto-generated if not specified)')
    parser.add_argument('--no-baseline', action='store_true', help='Hide baseline bars, show only measurement bars')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    # Validate input files
    if not Path(args.baseline_file).exists():
        print(f"❌ Baseline file '{args.baseline_file}' does not exist")
        sys.exit(1)
    
    if not Path(args.measurement_file).exists():
        print(f"❌ Measurement file '{args.measurement_file}' does not exist")
        sys.exit(1)
    
    # Create comparator
    comparator = EnergyPlusCommandLineComparator(
        baseline_file=args.baseline_file,
        measurement_file=args.measurement_file,
        output_file=args.output,
        show_baseline=not args.no_baseline
    )
    
    # Run comparison
    try:
        if not comparator.load_data():
            sys.exit(1)
        
        if not comparator.prepare_comparison_data():
            sys.exit(1)
        
        if not comparator.create_visualization():
            sys.exit(1)
        
        if not args.quiet:
            comparator.print_summary()
        
        print(f"\n✅ Successfully created comparison visualization: {comparator.output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()