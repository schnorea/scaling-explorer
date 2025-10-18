"""
Visualization and analysis tools for EnergyPlus profiling data
Creates charts and reports to analyze performance bottlenecks
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

class EnergyPlusProfilerAnalyzer:
    """
    Analyzes and visualizes EnergyPlus profiling data
    """
    
    def __init__(self, data_file: str = "energyplus_profiling_data.json"):
        self.data_file = data_file
        self.data = None
        self.load_data()
        
    def load_data(self):
        """Load profiling data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            print(f"Loaded profiling data from {self.data_file}")
        except FileNotFoundError:
            print(f"Data file {self.data_file} not found. Please generate data first.")
            return False
        return True
    
    def create_performance_charts(self):
        """Create comprehensive performance visualization charts"""
        if not self.data:
            return
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig = plt.figure(figsize=(20, 16))
        
        # Chart 1: Top 10 Time Consumers (Bar Chart)
        ax1 = plt.subplot(2, 3, 1)
        functions_data = self.data['functions']
        sorted_functions = sorted(functions_data.items(), 
                                key=lambda x: x[1]['total_time'], 
                                reverse=True)[:10]
        
        func_names = [name.replace('Calc', '').replace('Simulate', 'Sim') for name, _ in sorted_functions]
        times = [data['total_time'] for _, data in sorted_functions]
        
        bars = ax1.barh(func_names, times, color=plt.cm.viridis(np.linspace(0, 1, len(times))))
        ax1.set_xlabel('Time (seconds)')
        ax1.set_title('Top 10 Time-Consuming Functions')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add time labels on bars
        for i, (bar, time) in enumerate(zip(bars, times)):
            ax1.text(time + 0.5, i, f'{time:.1f}s', va='center', ha='left', fontsize=9)
        
        # Chart 2: Function Call Distribution (Pie Chart)
        ax2 = plt.subplot(2, 3, 2)
        top_categories = {
            'HVAC Systems': ['SimulateHVAC', 'CalcAirLoopSplitter', 'SimulateAirLoopComponents', 
                           'CalcFanSystemTemperatures', 'SimulateCoils', 'CalcCoolingCoil', 
                           'CalcHeatingCoil', 'SimulateChillers', 'CalcBoilerModel', 'SimulatePumps'],
            'Heat Balance': ['CalcHeatBalFiniteDiff', 'CalcHeatBalConductionTransferFunction',
                           'CalcWindowHeatBalance', 'CalcExteriorSurfaceTemp', 'CalcInteriorSurfaceTemp'],
            'Zone Equipment': ['ManageZoneEquipment', 'CalcZoneAirLoads', 'SimulateInternalHeatGains'],
            'Plant Systems': ['ManagePlantLoops', 'SimulatePlantProfile', 'UpdatePlantLoopInterface', 'CalcPlantValves'],
            'Weather/Solar': ['ManageWeather', 'CalcSolarRadiation', 'CalcDifferenceSolarRadiation'],
            'Utilities': ['PsyRhoAirFnPbTdbW', 'PsyHFnTdbW', 'POLYF', 'CurveValue', 'TableLookup'],
            'Other': []
        }
        
        category_times = {}
        for category, func_list in top_categories.items():
            total_time = sum(functions_data.get(func_name, {}).get('total_time', 0) 
                           for func_name in func_list)
            if total_time > 0:
                category_times[category] = total_time
        
        # Add remaining functions to "Other"
        accounted_functions = set()
        for func_list in top_categories.values():
            accounted_functions.update(func_list)
        
        other_time = sum(data['total_time'] for name, data in functions_data.items() 
                        if name not in accounted_functions)
        if other_time > 0:
            category_times['Other'] = other_time
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_times)))
        wedges, texts, autotexts = ax2.pie(category_times.values(), 
                                          labels=category_times.keys(),
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90)
        ax2.set_title('Time Distribution by Function Category')
        
        # Chart 3: Call Frequency vs Average Time (Scatter Plot)
        ax3 = plt.subplot(2, 3, 3)
        call_counts = [data['call_count'] for data in functions_data.values()]
        avg_times = [data['avg_time_per_call'] * 1000 for data in functions_data.values()]  # Convert to ms
        func_names_short = [name[:15] + '...' if len(name) > 15 else name 
                           for name in functions_data.keys()]
        
        scatter = ax3.scatter(call_counts, avg_times, 
                            c=[data['total_time'] for data in functions_data.values()],
                            cmap='viridis', s=60, alpha=0.7)
        ax3.set_xlabel('Number of Calls')
        ax3.set_ylabel('Average Time per Call (ms)')
        ax3.set_title('Call Frequency vs Average Time per Call')
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('Total Time (s)')
        
        # Chart 4: Time Series Simulation (Cumulative Time)
        ax4 = plt.subplot(2, 3, 4)
        # Simulate a time progression through the simulation
        simulation_phases = {
            'Initialization': ['GetInput', 'InitializeSimulation', 'SetupNodeVarsForReporting', 
                             'SetupOutputVariables', 'ValidateInputData'],
            'Weather Processing': ['ManageWeather', 'CalcSolarRadiation'],
            'Zone Calculations': ['CalcZoneAirLoads', 'CalcWindowHeatBalance', 'SimulateInternalHeatGains'],
            'HVAC Simulation': ['SimulateHVAV', 'SimulateAirLoopComponents', 'SimulateCoils'],
            'Plant Systems': ['ManagePlantLoops', 'SimulateChillers', 'CalcBoilerModel'],
            'Heat Balance': ['CalcHeatBalFiniteDiff', 'CalcHeatBalConductionTransferFunction'],
            'Reporting': ['UpdateDataandReport', 'WriteOutputToSQLite', 'UpdateMeterReporting']
        }
        
        phase_times = []
        phase_labels = []
        cumulative_time = 0
        
        for phase, func_list in simulation_phases.items():
            phase_time = sum(functions_data.get(func_name, {}).get('total_time', 0) 
                           for func_name in func_list)
            if phase_time > 0:
                cumulative_time += phase_time
                phase_times.append(cumulative_time)
                phase_labels.append(phase)
        
        ax4.plot(range(len(phase_times)), phase_times, 'o-', linewidth=2, markersize=8)
        ax4.set_xlabel('Simulation Phase')
        ax4.set_ylabel('Cumulative Time (seconds)')
        ax4.set_title('Simulated Time Progression Through Simulation')
        ax4.set_xticks(range(len(phase_labels)))
        ax4.set_xticklabels(phase_labels, rotation=45, ha='right')
        ax4.grid(True, alpha=0.3)
        
        # Chart 5: Performance Efficiency Analysis
        ax5 = plt.subplot(2, 3, 5)
        # Calculate efficiency metric (total work done / time spent)
        efficiency_data = []
        for name, data in functions_data.items():
            if data['call_count'] > 100:  # Focus on frequently called functions
                efficiency = data['call_count'] / data['total_time']  # calls per second
                efficiency_data.append((name, efficiency, data['total_time']))
        
        efficiency_data.sort(key=lambda x: x[1], reverse=True)
        top_efficient = efficiency_data[:10]
        
        names = [item[0][:12] + '...' if len(item[0]) > 12 else item[0] for item in top_efficient]
        efficiencies = [item[1] for item in top_efficient]
        
        bars = ax5.bar(range(len(names)), efficiencies, 
                      color=plt.cm.plasma(np.linspace(0, 1, len(names))))
        ax5.set_xlabel('Function')
        ax5.set_ylabel('Efficiency (calls/second)')
        ax5.set_title('Most Efficient Functions')
        ax5.set_xticks(range(len(names)))
        ax5.set_xticklabels(names, rotation=45, ha='right')
        ax5.grid(axis='y', alpha=0.3)
        
        # Chart 6: Standard Deviation Analysis (Performance Consistency)
        ax6 = plt.subplot(2, 3, 6)
        std_devs = []
        func_names_std = []
        total_times_std = []
        
        for name, data in functions_data.items():
            if data['std_deviation'] > 0 and data['call_count'] > 10:
                std_devs.append(data['std_deviation'] * 1000)  # Convert to ms
                func_names_std.append(name[:10] + '...' if len(name) > 10 else name)
                total_times_std.append(data['total_time'])
        
        # Sort by standard deviation
        combined = list(zip(std_devs, func_names_std, total_times_std))
        combined.sort(reverse=True)
        if len(combined) > 15:
            combined = combined[:15]
        
        std_devs, func_names_std, total_times_std = zip(*combined)
        
        scatter = ax6.scatter(range(len(std_devs)), std_devs, 
                            c=total_times_std, cmap='coolwarm', s=100, alpha=0.7)
        ax6.set_xlabel('Function (ranked by variability)')
        ax6.set_ylabel('Standard Deviation (ms)')
        ax6.set_title('Performance Variability Analysis')
        ax6.set_xticks(range(len(func_names_std)))
        ax6.set_xticklabels(func_names_std, rotation=45, ha='right')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('energyplus_performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Performance analysis charts saved as 'energyplus_performance_analysis.png'")
    
    def generate_detailed_report(self):
        """Generate a detailed text report of the profiling analysis"""
        if not self.data:
            return
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("EnergyPlus Simulation Performance Analysis Report")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Metadata
        metadata = self.data['metadata']
        report_lines.append("SIMULATION METADATA:")
        report_lines.append("-" * 20)
        for key, value in metadata.items():
            report_lines.append(f"{key.replace('_', ' ').title()}: {value}")
        report_lines.append("")
        
        # Summary statistics
        summary = self.data['summary']
        report_lines.append("PERFORMANCE SUMMARY:")
        report_lines.append("-" * 20)
        report_lines.append(f"Total Simulation Time: {summary['total_simulation_time']:.2f} seconds")
        report_lines.append(f"Total Function Calls: {summary['total_function_calls']:,}")
        report_lines.append("")
        
        # Performance bottlenecks
        report_lines.append("PERFORMANCE BOTTLENECKS:")
        report_lines.append("-" * 25)
        functions_data = self.data['functions']
        
        # Functions taking more than 5% of total time
        bottlenecks = [(name, data) for name, data in functions_data.items() 
                      if data['percentage_of_total'] > 5.0]
        bottlenecks.sort(key=lambda x: x[1]['total_time'], reverse=True)
        
        for name, data in bottlenecks:
            report_lines.append(f"• {name}:")
            report_lines.append(f"  - Total Time: {data['total_time']:.2f}s ({data['percentage_of_total']:.1f}%)")
            report_lines.append(f"  - Calls: {data['call_count']:,}")
            report_lines.append(f"  - Avg per Call: {data['avg_time_per_call']*1000:.2f}ms")
            report_lines.append("")
        
        # Optimization recommendations
        report_lines.append("OPTIMIZATION RECOMMENDATIONS:")
        report_lines.append("-" * 30)
        
        # High time, low call count functions
        optimization_candidates = [(name, data) for name, data in functions_data.items()
                                 if data['total_time'] > 5.0 and data['call_count'] < 1000]
        optimization_candidates.sort(key=lambda x: x[1]['avg_time_per_call'], reverse=True)
        
        if optimization_candidates:
            report_lines.append("1. Functions with high per-call overhead:")
            for name, data in optimization_candidates[:5]:
                report_lines.append(f"   • {name}: {data['avg_time_per_call']*1000:.2f}ms per call")
            report_lines.append("")
        
        # High variability functions
        high_variability = [(name, data) for name, data in functions_data.items()
                          if data['std_deviation'] > data['avg_time_per_call'] * 0.5 and data['call_count'] > 100]
        high_variability.sort(key=lambda x: x[1]['std_deviation'], reverse=True)
        
        if high_variability:
            report_lines.append("2. Functions with inconsistent performance:")
            for name, data in high_variability[:5]:
                cv = (data['std_deviation'] / data['avg_time_per_call']) * 100  # Coefficient of variation
                report_lines.append(f"   • {name}: CV = {cv:.1f}%")
            report_lines.append("")
        
        # Frequently called utility functions
        utility_functions = [(name, data) for name, data in functions_data.items()
                           if data['call_count'] > 10000]
        utility_functions.sort(key=lambda x: x[1]['call_count'], reverse=True)
        
        if utility_functions:
            report_lines.append("3. Most frequently called utility functions (optimization targets):")
            for name, data in utility_functions[:5]:
                total_overhead = data['call_count'] * data['avg_time_per_call']
                report_lines.append(f"   • {name}: {data['call_count']:,} calls, "
                                  f"{total_overhead:.2f}s total overhead")
            report_lines.append("")
        
        # Save report
        report_text = "\n".join(report_lines)
        with open("energyplus_performance_report.txt", "w") as f:
            f.write(report_text)
        
        print(report_text)
        print(f"\nDetailed report saved to 'energyplus_performance_report.txt'")


def main():
    """Main function to run the analysis"""
    analyzer = EnergyPlusProfilerAnalyzer()
    
    if analyzer.data:
        analyzer.create_performance_charts()
        analyzer.generate_detailed_report()
    else:
        print("Please run energyplus_profiling_data.py first to generate the profiling data.")


if __name__ == "__main__":
    main()