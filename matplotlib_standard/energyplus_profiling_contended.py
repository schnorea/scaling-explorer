"""
Fictional profiling data for EnergyPlus simulation application under memory contention
Represents timing measurements showing performance degradation due to resource contention,
cache thrashing, swap to disk, and other applications competing for system resources
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

class EnergyPlusContentionProfiler:
    """
    Simulates profiling data for EnergyPlus under memory contention conditions
    Shows realistic performance degradation patterns
    """
    
    def __init__(self):
        self.profiling_data = {}
        self.simulation_metadata = {
            "building_type": "Commercial Office",
            "climate_zone": "4A", 
            "simulation_period": "Annual",
            "timestep": "4 per hour",
            "total_simulation_time": 0.0,
            "system_conditions": {
                "memory_pressure": "High",
                "concurrent_applications": ["Chrome (2.1GB)", "Docker (1.8GB)", "IntelliJ IDEA (1.2GB)", "Slack (450MB)"],
                "available_memory": "1.2GB of 16GB",
                "swap_activity": "Heavy (2.3GB active)",
                "cache_hit_ratio": "64%",  # Degraded from typical 85-90%
                "page_faults_per_second": 1250,
                "context_switches_per_second": 8900
            }
        }
        
    def generate_profiling_data(self) -> Dict:
        """Generate realistic profiling data showing memory contention effects"""
        
        # Apply contention multipliers based on function characteristics
        # Memory-intensive functions suffer more from cache thrashing
        # I/O functions suffer more from swap activity
        # Computation functions suffer from context switches
        
        function_profiles = {
            # HVAC System Functions - moderate memory usage, frequent access
            "SimulateHVAC": self._generate_contended_data(45.2, 12.3, 850, 
                                                         contention_factor=2.8, variability_increase=3.2),
            "CalcAirLoopSplitter": self._generate_contended_data(2.1, 0.5, 1200,
                                                               contention_factor=2.1, variability_increase=2.8),
            "SimulateAirLoopComponents": self._generate_contended_data(18.7, 4.2, 950,
                                                                     contention_factor=2.6, variability_increase=3.1),
            "CalcFanSystemTemperatures": self._generate_contended_data(3.4, 0.8, 1100,
                                                                     contention_factor=2.3, variability_increase=2.9),
            "SimulateCoils": self._generate_contended_data(8.9, 2.1, 1050,
                                                         contention_factor=2.4, variability_increase=3.0),
            "CalcCoolingCoil": self._generate_contended_data(5.2, 1.3, 920,
                                                           contention_factor=2.2, variability_increase=2.7),
            "CalcHeatingCoil": self._generate_contended_data(4.1, 0.9, 880,
                                                           contention_factor=2.1, variability_increase=2.6),
            "SimulateChillers": self._generate_contended_data(12.5, 3.7, 450,
                                                            contention_factor=3.2, variability_increase=4.1),
            "CalcBoilerModel": self._generate_contended_data(6.8, 1.8, 380,
                                                           contention_factor=2.9, variability_increase=3.4),
            "SimulatePumps": self._generate_contended_data(2.9, 0.7, 760,
                                                         contention_factor=2.0, variability_increase=2.5),
            
            # Zone and Surface Functions - heavy memory access patterns
            "ManageZoneEquipment": self._generate_contended_data(15.6, 4.5, 1200,
                                                               contention_factor=3.1, variability_increase=3.8),
            "CalcZoneAirLoads": self._generate_contended_data(22.1, 6.2, 1150,
                                                            contention_factor=3.4, variability_increase=4.2),
            "SimulateInternalHeatGains": self._generate_contended_data(7.3, 2.0, 1100,
                                                                     contention_factor=2.7, variability_increase=3.2),
            "CalcWindowHeatBalance": self._generate_contended_data(19.8, 5.4, 980,
                                                                 contention_factor=4.1, variability_increase=5.2),
            "CalcExteriorSurfaceTemp": self._generate_contended_data(8.7, 2.3, 1050,
                                                                   contention_factor=3.3, variability_increase=4.0),
            "CalcInteriorSurfaceTemp": self._generate_contended_data(11.2, 3.1, 1020,
                                                                   contention_factor=3.5, variability_increase=4.3),
            
            # Heat Balance - most memory intensive, severe cache thrashing
            "CalcHeatBalFiniteDiff": self._generate_contended_data(31.4, 9.8, 720,
                                                                 contention_factor=4.8, variability_increase=6.1),
            "CalcHeatBalConductionTransferFunction": self._generate_contended_data(25.7, 7.1, 680,
                                                                                 contention_factor=4.5, variability_increase=5.8),
            
            # Weather and Solar Functions - moderate impact
            "ManageWeather": self._generate_contended_data(1.8, 0.4, 8760,
                                                         contention_factor=1.6, variability_increase=2.1),
            "CalcSolarRadiation": self._generate_contended_data(13.5, 3.8, 1200,
                                                              contention_factor=2.8, variability_increase=3.4),
            "CalcDifferenceSolarRadiation": self._generate_contended_data(4.2, 1.1, 1150,
                                                                        contention_factor=2.4, variability_increase=2.9),
            "InterpolateBetweenTwoValues": self._generate_contended_data(0.05, 0.01, 15600,
                                                                       contention_factor=1.8, variability_increase=2.3),
            "CalculateSunDirectionCosines": self._generate_contended_data(0.8, 0.2, 8760,
                                                                        contention_factor=1.7, variability_increase=2.2),
            
            # Plant Loop Functions - moderate to heavy memory usage
            "ManagePlantLoops": self._generate_contended_data(28.9, 8.2, 650,
                                                            contention_factor=3.9, variability_increase=4.8),
            "SimulatePlantProfile": self._generate_contended_data(3.7, 1.0, 750,
                                                                contention_factor=2.5, variability_increase=3.1),
            "UpdatePlantLoopInterface": self._generate_contended_data(2.1, 0.6, 890,
                                                                    contention_factor=2.2, variability_increase=2.8),
            "CalcPlantValves": self._generate_contended_data(1.9, 0.5, 420,
                                                           contention_factor=2.0, variability_increase=2.5),
            
            # Economics and Utility Functions - light memory usage
            "CalcTariffEvaluation": self._generate_contended_data(5.1, 1.4, 120,
                                                                contention_factor=1.8, variability_increase=2.2),
            "UpdateUtilityBills": self._generate_contended_data(2.3, 0.6, 140,
                                                              contention_factor=1.7, variability_increase=2.1),
            "EconomicTariffManager": self._generate_contended_data(3.8, 1.0, 110,
                                                                 contention_factor=1.9, variability_increase=2.3),
            
            # Output and Reporting Functions - I/O intensive, affected by swap
            "UpdateDataandReport": self._generate_contended_data(12.4, 3.5, 200,
                                                               contention_factor=3.7, variability_increase=4.5),
            "WriteOutputToSQLite": self._generate_contended_data(8.7, 2.2, 180,
                                                               contention_factor=4.2, variability_increase=5.1),
            "ReportSurfaceHeatBalance": self._generate_contended_data(4.6, 1.2, 195,
                                                                    contention_factor=3.1, variability_increase=3.8),
            "ReportAirHeatBalance": self._generate_contended_data(3.9, 1.0, 190,
                                                                contention_factor=2.9, variability_increase=3.5),
            "UpdateMeterReporting": self._generate_contended_data(2.1, 0.5, 210,
                                                                contention_factor=2.6, variability_increase=3.2),
            
            # Initialization and Setup Functions - less affected (run once)
            "GetInput": self._generate_contended_data(15.7, 0.0, 1,
                                                    contention_factor=2.1, variability_increase=1.0),
            "InitializeSimulation": self._generate_contended_data(8.3, 0.0, 1,
                                                                contention_factor=2.3, variability_increase=1.0),
            "SetupNodeVarsForReporting": self._generate_contended_data(2.4, 0.0, 1,
                                                                     contention_factor=1.8, variability_increase=1.0),
            "SetupOutputVariables": self._generate_contended_data(3.1, 0.0, 1,
                                                                contention_factor=1.9, variability_increase=1.0),
            "ValidateInputData": self._generate_contended_data(4.8, 0.0, 1,
                                                             contention_factor=2.0, variability_increase=1.0),
            
            # Psychrometric Functions - very frequent, cache sensitive
            "PsyRhoAirFnPbTdbW": self._generate_contended_data(0.02, 0.005, 45000,
                                                             contention_factor=2.4, variability_increase=3.8),
            "PsyHFnTdbW": self._generate_contended_data(0.015, 0.003, 52000,
                                                      contention_factor=2.3, variability_increase=3.6),
            "PsyCpAirFnW": self._generate_contended_data(0.012, 0.002, 38000,
                                                       contention_factor=2.2, variability_increase=3.4),
            "PsyTsatFnHPb": self._generate_contended_data(0.018, 0.004, 28000,
                                                        contention_factor=2.5, variability_increase=3.9),
            
            # Mathematical Utility Functions - extremely frequent, severe cache impact
            "POLYF": self._generate_contended_data(0.008, 0.001, 125000,
                                                 contention_factor=3.1, variability_increase=4.7),
            "CurveValue": self._generate_contended_data(0.012, 0.002, 89000,
                                                      contention_factor=2.9, variability_increase=4.3),
            "TableLookup": self._generate_contended_data(0.025, 0.005, 67000,
                                                       contention_factor=3.4, variability_increase=5.2),
            "RegularQn": self._generate_contended_data(0.035, 0.008, 34000,
                                                     contention_factor=2.7, variability_increase=3.9),
        }
        
        # Calculate total simulation time
        total_time = sum(data["total_time"] for data in function_profiles.values())
        self.simulation_metadata["total_simulation_time"] = total_time
        
        self.profiling_data = {
            "metadata": self.simulation_metadata,
            "timestamp": datetime.now().isoformat(),
            "functions": function_profiles,
            "summary": self._generate_summary(function_profiles)
        }
        
        return self.profiling_data
    
    def _generate_contended_data(self, baseline_time: float, baseline_std: float, 
                               call_count: int, contention_factor: float, 
                               variability_increase: float) -> Dict:
        """Generate function timing data with memory contention effects"""
        
        # Apply contention factor to increase execution time
        contended_time = baseline_time * contention_factor
        
        # Increase variability due to inconsistent resource availability
        contended_std = baseline_std * variability_increase
        
        # Add some variability to call counts (some functions may be called less due to timeouts)
        actual_calls = max(1, int(call_count * random.uniform(0.92, 1.03)))
        
        # Generate individual call times with higher variability
        if actual_calls > 0:
            avg_per_call = contended_time / actual_calls
            std_per_call = contended_std / actual_calls if actual_calls > 1 else 0
            
            # Add occasional extreme outliers due to swap events or severe cache misses
            call_times = []
            for _ in range(min(100, actual_calls)):
                base_time = max(0.001, random.normalvariate(avg_per_call, std_per_call))
                
                # 5% chance of extreme slowdown (swap event or major cache miss)
                if random.random() < 0.05:
                    base_time *= random.uniform(5, 15)  # 5-15x slowdown
                # 15% chance of moderate slowdown (minor cache miss or context switch)
                elif random.random() < 0.15:
                    base_time *= random.uniform(2, 4)   # 2-4x slowdown
                
                call_times.append(base_time)
        else:
            call_times = []
        
        # Add random variation to total time
        total_time = contended_time + random.normalvariate(0, contended_std * 0.15)
        total_time = max(0.001, total_time)
        
        avg_per_call = total_time / actual_calls if actual_calls > 0 else total_time
        
        return {
            "total_time": round(total_time, 6),
            "call_count": actual_calls,
            "avg_time_per_call": round(avg_per_call, 6),
            "min_time": round(min(call_times) if call_times else avg_per_call, 6),
            "max_time": round(max(call_times) if call_times else avg_per_call, 6),
            "std_deviation": round(contended_std / actual_calls if actual_calls > 1 else 0, 6),
            "percentage_of_total": 0.0,  # Will be calculated in summary
            "contention_metrics": {
                "baseline_time": round(baseline_time, 6),
                "contention_factor": round(contention_factor, 2),
                "performance_degradation_percent": round((contention_factor - 1) * 100, 1),
                "variability_increase_factor": round(variability_increase, 2)
            }
        }
    
    def _generate_summary(self, function_profiles: Dict) -> Dict:
        """Generate summary statistics including contention analysis"""
        total_simulation_time = sum(data["total_time"] for data in function_profiles.values())
        total_function_calls = sum(data["call_count"] for data in function_profiles.values())
        baseline_total_time = sum(data["contention_metrics"]["baseline_time"] for data in function_profiles.values())
        
        # Update percentage of total time for each function
        for func_data in function_profiles.values():
            func_data["percentage_of_total"] = round(
                (func_data["total_time"] / total_simulation_time) * 100, 2
            )
        
        # Find top time consumers
        sorted_functions = sorted(
            function_profiles.items(), 
            key=lambda x: x[1]["total_time"], 
            reverse=True
        )
        
        # Calculate contention impact metrics
        overall_degradation = ((total_simulation_time - baseline_total_time) / baseline_total_time) * 100
        
        # Find most impacted functions
        most_impacted = sorted(
            function_profiles.items(),
            key=lambda x: x[1]["contention_metrics"]["performance_degradation_percent"],
            reverse=True
        )
        
        return {
            "total_simulation_time": round(total_simulation_time, 3),
            "baseline_simulation_time": round(baseline_total_time, 3),
            "overall_performance_degradation_percent": round(overall_degradation, 1),
            "additional_time_due_to_contention": round(total_simulation_time - baseline_total_time, 3),
            "total_function_calls": total_function_calls,
            "top_5_time_consumers": [
                {
                    "function": func_name,
                    "time": func_data["total_time"],
                    "percentage": func_data["percentage_of_total"],
                    "degradation_percent": func_data["contention_metrics"]["performance_degradation_percent"]
                }
                for func_name, func_data in sorted_functions[:5]
            ],
            "most_impacted_by_contention": [
                {
                    "function": func_name,
                    "degradation_percent": func_data["contention_metrics"]["performance_degradation_percent"],
                    "time_increase": round(func_data["total_time"] - func_data["contention_metrics"]["baseline_time"], 3)
                }
                for func_name, func_data in most_impacted[:5]
            ],
            "most_called_functions": sorted([
                {
                    "function": func_name,
                    "calls": func_data["call_count"],
                    "avg_time": func_data["avg_time_per_call"]
                }
                for func_name, func_data in function_profiles.items()
            ], key=lambda x: x["calls"], reverse=True)[:5]
        }
    
    def save_to_json(self, filename: str = "energyplus_profiling_contended.json"):
        """Save contended profiling data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.profiling_data, f, indent=2)
        print(f"Contended profiling data saved to {filename}")
    
    def print_summary(self):
        """Print a formatted summary of contended profiling data"""
        if not self.profiling_data:
            self.generate_profiling_data()
        
        summary = self.profiling_data["summary"]
        metadata = self.profiling_data["metadata"]
        
        print("\n" + "="*70)
        print("EnergyPlus Simulation Performance Profile - MEMORY CONTENTION")
        print("="*70)
        print(f"Building Type: {metadata['building_type']}")
        print(f"Climate Zone: {metadata['climate_zone']}")
        print(f"System Memory Pressure: {metadata['system_conditions']['memory_pressure']}")
        print(f"Available Memory: {metadata['system_conditions']['available_memory']}")
        print(f"Cache Hit Ratio: {metadata['system_conditions']['cache_hit_ratio']}")
        print(f"Swap Activity: {metadata['system_conditions']['swap_activity']}")
        print()
        print(f"Total Simulation Time: {summary['total_simulation_time']:.2f} seconds")
        print(f"Baseline Time (no contention): {summary['baseline_simulation_time']:.2f} seconds")
        print(f"Performance Degradation: {summary['overall_performance_degradation_percent']:.1f}%")
        print(f"Additional Time Due to Contention: {summary['additional_time_due_to_contention']:.2f} seconds")
        print(f"Total Function Calls: {summary['total_function_calls']:,}")
        
        print(f"\nTop 5 Time-Consuming Functions (with degradation):")
        print("-" * 60)
        for i, func in enumerate(summary["top_5_time_consumers"], 1):
            print(f"{i}. {func['function']:<35} {func['time']:>8.2f}s ({func['percentage']:>5.1f}%) "
                  f"[+{func['degradation_percent']:>5.1f}%]")
        
        print(f"\nMost Impacted by Memory Contention:")
        print("-" * 50)
        for i, func in enumerate(summary["most_impacted_by_contention"], 1):
            print(f"{i}. {func['function']:<35} +{func['degradation_percent']:>5.1f}% "
                  f"(+{func['time_increase']:>5.2f}s)")
        
        print(f"\nConcurrent Applications:")
        for app in metadata['system_conditions']['concurrent_applications']:
            print(f"  • {app}")


def main():
    """Generate and display EnergyPlus contended profiling data"""
    profiler = EnergyPlusContentionProfiler()
    profiler.generate_profiling_data()
    profiler.print_summary()
    profiler.save_to_json()


if __name__ == "__main__":
    main()