"""
Fictional profiling data for EnergyPlus simulation with multithreading improvements
but also suffering from memory contention issues simultaneously.
This represents a realistic scenario where threading optimizations are partially
offset by system memory pressure from concurrent applications.
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

class EnergyPlusHybridProfiler:
    """
    Simulates profiling data for EnergyPlus with both threading improvements
    AND memory contention issues occurring simultaneously
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
                "cpu_cores": 8,
                "threads_available": 16,
                "thread_pool_size": 6,
                "memory_pressure": "High",
                "available_memory": "2.1GB of 16GB",
                "cache_hit_ratio": "71%",  # Degraded from optimal but better than severe contention
                "swap_activity": "Moderate (1.4GB active)",
                "page_faults_per_second": 850,
                "context_switches_per_second": 12500,  # Higher due to threading + contention
                "concurrent_applications": ["Chrome (1.8GB)", "Docker (1.2GB)", "Visual Studio (950MB)", "Teams (380MB)"],
                "threading_efficiency_degradation": "25%",  # Threading less effective under memory pressure
                "scenario": "Multithreaded with Memory Contention"
            }
        }
        
    def generate_profiling_data(self) -> Dict:
        """Generate realistic profiling data showing both threading gains and memory contention losses"""
        
        # This scenario applies BOTH effects:
        # 1. Threading improvements (but reduced efficiency due to memory pressure)
        # 2. Memory contention slowdowns
        # The net result varies by function type
        
        function_profiles = {
            # HVAC System Functions - moderate threading gains, moderate contention impact
            "SimulateHVAC": self._generate_hybrid_data(45.2, 12.3, 850,
                                                      thread_improvement=1.8, thread_efficiency=0.60,  # Reduced from 0.75
                                                      contention_factor=2.1, net_effect="mixed"),
            "CalcAirLoopSplitter": self._generate_hybrid_data(2.1, 0.5, 1200,
                                                             thread_improvement=2.2, thread_efficiency=0.65,  # Reduced from 0.85
                                                             contention_factor=1.8, net_effect="slight_gain"),
            "SimulateAirLoopComponents": self._generate_hybrid_data(18.7, 4.2, 950,
                                                                   thread_improvement=2.4, thread_efficiency=0.62,  # Reduced from 0.80
                                                                   contention_factor=2.0, net_effect="mixed"),
            "CalcFanSystemTemperatures": self._generate_hybrid_data(3.4, 0.8, 1100,
                                                                   thread_improvement=1.9, thread_efficiency=0.58,  # Reduced from 0.70
                                                                   contention_factor=1.9, net_effect="neutral"),
            "SimulateCoils": self._generate_hybrid_data(8.9, 2.1, 1050,
                                                       thread_improvement=2.1, thread_efficiency=0.60,  # Reduced from 0.78
                                                       contention_factor=1.9, net_effect="slight_gain"),
            "CalcCoolingCoil": self._generate_hybrid_data(5.2, 1.3, 920,
                                                         thread_improvement=2.0, thread_efficiency=0.55,  # Reduced from 0.76
                                                         contention_factor=1.8, net_effect="slight_gain"),
            "CalcHeatingCoil": self._generate_hybrid_data(4.1, 0.9, 880,
                                                         thread_improvement=1.8, thread_efficiency=0.52,  # Reduced from 0.74
                                                         contention_factor=1.7, net_effect="slight_gain"),
            "SimulateChillers": self._generate_hybrid_data(12.5, 3.7, 450,
                                                          thread_improvement=1.6, thread_efficiency=0.45,  # Reduced from 0.65
                                                          contention_factor=2.4, net_effect="loss"),
            "CalcBoilerModel": self._generate_hybrid_data(6.8, 1.8, 380,
                                                         thread_improvement=1.5, thread_efficiency=0.40,  # Reduced from 0.60
                                                         contention_factor=2.2, net_effect="loss"),
            "SimulatePumps": self._generate_hybrid_data(2.9, 0.7, 760,
                                                       thread_improvement=1.4, thread_efficiency=0.35,  # Reduced from 0.55
                                                       contention_factor=1.8, net_effect="slight_loss"),
            
            # Zone and Surface Functions - high threading potential but also high memory usage
            "ManageZoneEquipment": self._generate_hybrid_data(15.6, 4.5, 1200,
                                                             thread_improvement=3.2, thread_efficiency=0.68,  # Reduced from 0.90
                                                             contention_factor=2.3, net_effect="gain"),
            "CalcZoneAirLoads": self._generate_hybrid_data(22.1, 6.2, 1150,
                                                          thread_improvement=3.8, thread_efficiency=0.70,  # Reduced from 0.92
                                                          contention_factor=2.5, net_effect="gain"),
            "SimulateInternalHeatGains": self._generate_hybrid_data(7.3, 2.0, 1100,
                                                                   thread_improvement=2.9, thread_efficiency=0.65,  # Reduced from 0.88
                                                                   contention_factor=2.1, net_effect="gain"),
            "CalcWindowHeatBalance": self._generate_hybrid_data(19.8, 5.4, 980,
                                                              thread_improvement=4.2, thread_efficiency=0.72,  # Reduced from 0.95
                                                              contention_factor=2.8, net_effect="gain"),
            "CalcExteriorSurfaceTemp": self._generate_hybrid_data(8.7, 2.3, 1050,
                                                                 thread_improvement=3.5, thread_efficiency=0.68,  # Reduced from 0.91
                                                                 contention_factor=2.4, net_effect="gain"),
            "CalcInteriorSurfaceTemp": self._generate_hybrid_data(11.2, 3.1, 1020,
                                                                 thread_improvement=3.6, thread_efficiency=0.70,  # Reduced from 0.92
                                                                 contention_factor=2.5, net_effect="gain"),
            
            # Heat Balance - excellent threading potential but severe memory impact
            "CalcHeatBalFiniteDiff": self._generate_hybrid_data(31.4, 9.8, 720,
                                                              thread_improvement=4.8, thread_efficiency=0.65,  # Reduced from 0.96
                                                              contention_factor=3.2, net_effect="mixed"),
            "CalcHeatBalConductionTransferFunction": self._generate_hybrid_data(25.7, 7.1, 680,
                                                                               thread_improvement=4.5, thread_efficiency=0.63,  # Reduced from 0.94
                                                                               contention_factor=3.0, net_effect="mixed"),
            
            # Weather and Solar Functions - limited threading, moderate contention
            "ManageWeather": self._generate_hybrid_data(1.8, 0.4, 8760,
                                                       thread_improvement=1.1, thread_efficiency=0.20,  # Reduced from 0.30
                                                       contention_factor=1.4, net_effect="loss"),
            "CalcSolarRadiation": self._generate_hybrid_data(13.5, 3.8, 1200,
                                                            thread_improvement=2.8, thread_efficiency=0.62,  # Reduced from 0.85
                                                            contention_factor=2.1, net_effect="gain"),
            "CalcDifferenceSolarRadiation": self._generate_hybrid_data(4.2, 1.1, 1150,
                                                                      thread_improvement=2.6, thread_efficiency=0.60,  # Reduced from 0.83
                                                                      contention_factor=1.9, net_effect="gain"),
            "InterpolateBetweenTwoValues": self._generate_hybrid_data(0.05, 0.01, 15600,
                                                                    thread_improvement=1.2, thread_efficiency=0.20,  # Reduced from 0.35
                                                                    contention_factor=1.6, net_effect="loss"),
            "CalculateSunDirectionCosines": self._generate_hybrid_data(0.8, 0.2, 8760,
                                                                     thread_improvement=1.3, thread_efficiency=0.25,  # Reduced from 0.40
                                                                     contention_factor=1.5, net_effect="loss"),
            
            # Plant Loop Functions - moderate threading, high memory contention
            "ManagePlantLoops": self._generate_hybrid_data(28.9, 8.2, 650,
                                                          thread_improvement=2.2, thread_efficiency=0.50,  # Reduced from 0.75
                                                          contention_factor=2.8, net_effect="loss"),
            "SimulatePlantProfile": self._generate_hybrid_data(3.7, 1.0, 750,
                                                              thread_improvement=1.8, thread_efficiency=0.45,  # Reduced from 0.68
                                                              contention_factor=2.0, net_effect="slight_loss"),
            "UpdatePlantLoopInterface": self._generate_hybrid_data(2.1, 0.6, 890,
                                                                  thread_improvement=1.4, thread_efficiency=0.35,  # Reduced from 0.52
                                                                  contention_factor=1.8, net_effect="loss"),
            "CalcPlantValves": self._generate_hybrid_data(1.9, 0.5, 420,
                                                         thread_improvement=1.6, thread_efficiency=0.38,  # Reduced from 0.58
                                                         contention_factor=1.7, net_effect="slight_loss"),
            
            # Economics and Utility Functions - minimal threading, low contention
            "CalcTariffEvaluation": self._generate_hybrid_data(5.1, 1.4, 120,
                                                              thread_improvement=1.2, thread_efficiency=0.25,  # Reduced from 0.38
                                                              contention_factor=1.5, net_effect="loss"),
            "UpdateUtilityBills": self._generate_hybrid_data(2.3, 0.6, 140,
                                                            thread_improvement=1.1, thread_efficiency=0.20,  # Reduced from 0.32
                                                            contention_factor=1.4, net_effect="loss"),
            "EconomicTariffManager": self._generate_hybrid_data(3.8, 1.0, 110,
                                                               thread_improvement=1.1, thread_efficiency=0.22,  # Reduced from 0.35
                                                               contention_factor=1.6, net_effect="loss"),
            
            # Output and Reporting Functions - limited threading, I/O contention
            "UpdateDataandReport": self._generate_hybrid_data(12.4, 3.5, 200,
                                                             thread_improvement=1.3, thread_efficiency=0.30,  # Reduced from 0.45
                                                             contention_factor=2.5, net_effect="loss"),
            "WriteOutputToSQLite": self._generate_hybrid_data(8.7, 2.2, 180,
                                                             thread_improvement=1.2, thread_efficiency=0.25,  # Reduced from 0.40
                                                             contention_factor=2.8, net_effect="loss"),
            "ReportSurfaceHeatBalance": self._generate_hybrid_data(4.6, 1.2, 195,
                                                                  thread_improvement=1.4, thread_efficiency=0.32,  # Reduced from 0.48
                                                                  contention_factor=2.2, net_effect="loss"),
            "ReportAirHeatBalance": self._generate_hybrid_data(3.9, 1.0, 190,
                                                              thread_improvement=1.3, thread_efficiency=0.30,  # Reduced from 0.46
                                                              contention_factor=2.0, net_effect="loss"),
            "UpdateMeterReporting": self._generate_hybrid_data(2.1, 0.5, 210,
                                                              thread_improvement=1.2, thread_efficiency=0.28,  # Reduced from 0.42
                                                              contention_factor=1.8, net_effect="loss"),
            
            # Initialization and Setup Functions - no threading, moderate contention
            "GetInput": self._generate_hybrid_data(15.7, 0.0, 1,
                                                  thread_improvement=1.0, thread_efficiency=0.0,
                                                  contention_factor=1.8, net_effect="loss"),
            "InitializeSimulation": self._generate_hybrid_data(8.3, 0.0, 1,
                                                              thread_improvement=1.0, thread_efficiency=0.0,
                                                              contention_factor=1.9, net_effect="loss"),
            "SetupNodeVarsForReporting": self._generate_hybrid_data(2.4, 0.0, 1,
                                                                   thread_improvement=1.0, thread_efficiency=0.0,
                                                                   contention_factor=1.5, net_effect="loss"),
            "SetupOutputVariables": self._generate_hybrid_data(3.1, 0.0, 1,
                                                              thread_improvement=1.0, thread_efficiency=0.0,
                                                              contention_factor=1.6, net_effect="loss"),
            "ValidateInputData": self._generate_hybrid_data(4.8, 0.0, 1,
                                                           thread_improvement=1.0, thread_efficiency=0.0,
                                                           contention_factor=1.7, net_effect="loss"),
            
            # Psychrometric Functions - good vectorization but cache sensitive
            "PsyRhoAirFnPbTdbW": self._generate_hybrid_data(0.02, 0.005, 45000,
                                                           thread_improvement=2.8, thread_efficiency=0.55,  # Reduced from 0.85
                                                           contention_factor=2.0, net_effect="slight_loss"),
            "PsyHFnTdbW": self._generate_hybrid_data(0.015, 0.003, 52000,
                                                    thread_improvement=2.9, thread_efficiency=0.57,  # Reduced from 0.87
                                                    contention_factor=1.9, net_effect="slight_loss"),
            "PsyCpAirFnW": self._generate_hybrid_data(0.012, 0.002, 38000,
                                                     thread_improvement=2.7, thread_efficiency=0.52,  # Reduced from 0.84
                                                     contention_factor=1.8, net_effect="slight_loss"),
            "PsyTsatFnHPb": self._generate_hybrid_data(0.018, 0.004, 28000,
                                                      thread_improvement=2.6, thread_efficiency=0.50,  # Reduced from 0.82
                                                      contention_factor=2.1, net_effect="slight_loss"),
            
            # Mathematical Utility Functions - excellent vectorization but very cache sensitive
            "POLYF": self._generate_hybrid_data(0.008, 0.001, 125000,
                                               thread_improvement=3.2, thread_efficiency=0.60,  # Reduced from 0.90
                                               contention_factor=2.3, net_effect="slight_loss"),
            "CurveValue": self._generate_hybrid_data(0.012, 0.002, 89000,
                                                    thread_improvement=3.0, thread_efficiency=0.58,  # Reduced from 0.88
                                                    contention_factor=2.2, net_effect="slight_loss"),
            "TableLookup": self._generate_hybrid_data(0.025, 0.005, 67000,
                                                     thread_improvement=2.4, thread_efficiency=0.50,  # Reduced from 0.78
                                                     contention_factor=2.5, net_effect="loss"),
            "RegularQn": self._generate_hybrid_data(0.035, 0.008, 34000,
                                                   thread_improvement=2.2, thread_efficiency=0.48,  # Reduced from 0.75
                                                   contention_factor=2.1, net_effect="slight_loss"),
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
    
    def _generate_hybrid_data(self, baseline_time: float, baseline_std: float, 
                            call_count: int, thread_improvement: float, thread_efficiency: float,
                            contention_factor: float, net_effect: str) -> Dict:
        """Generate function timing data with both threading improvements and memory contention"""
        
        # Calculate threading improvement (reduced by memory pressure)
        effective_thread_improvement = 1 + (thread_improvement - 1) * thread_efficiency
        
        # Apply both effects: threading improvement first, then contention slowdown
        threaded_time = baseline_time / effective_thread_improvement
        final_time = threaded_time * contention_factor
        
        # Calculate net effect
        net_performance_ratio = final_time / baseline_time
        
        # Increase variability due to both threading overhead and memory contention
        hybrid_std = baseline_std * 1.4  # Higher variability than either effect alone
        
        # Call counts may vary slightly due to timeouts or retries under contention
        actual_calls = max(1, int(call_count * random.uniform(0.96, 1.04)))
        
        # Generate individual call times with complex variability patterns
        if actual_calls > 0:
            avg_per_call = final_time / actual_calls
            std_per_call = hybrid_std / actual_calls if actual_calls > 1 else 0
            
            call_times = []
            for _ in range(min(100, actual_calls)):
                base_time = max(0.001, random.normalvariate(avg_per_call, std_per_call))
                
                # Occasional extreme events (memory pressure spikes)
                if random.random() < 0.03:
                    base_time *= random.uniform(8, 20)  # Severe memory pressure event
                # Threading synchronization delays
                elif random.random() < 0.08:
                    base_time *= random.uniform(2, 5)   # Thread synchronization overhead
                # Cache miss events
                elif random.random() < 0.12:
                    base_time *= random.uniform(1.5, 3) # Cache miss penalty
                
                call_times.append(base_time)
        else:
            call_times = []
        
        # Add random variation to total time
        total_time = final_time + random.normalvariate(0, hybrid_std * 0.12)
        total_time = max(0.001, total_time)
        
        avg_per_call = total_time / actual_calls if actual_calls > 0 else total_time
        
        return {
            "total_time": round(total_time, 6),
            "call_count": actual_calls,
            "avg_time_per_call": round(avg_per_call, 6),
            "min_time": round(min(call_times) if call_times else avg_per_call, 6),
            "max_time": round(max(call_times) if call_times else avg_per_call, 6),
            "std_deviation": round(hybrid_std / actual_calls if actual_calls > 1 else 0, 6),
            "percentage_of_total": 0.0,  # Will be calculated in summary
            "hybrid_metrics": {
                "baseline_time": round(baseline_time, 6),
                "thread_improvement_factor": round(thread_improvement, 2),
                "thread_efficiency": round(thread_efficiency, 2),
                "contention_factor": round(contention_factor, 2),
                "effective_thread_improvement": round(effective_thread_improvement, 2),
                "net_performance_ratio": round(net_performance_ratio, 2),
                "net_effect": net_effect,
                "time_saved_from_threading": round(baseline_time - (baseline_time / effective_thread_improvement), 6),
                "time_lost_to_contention": round((final_time - (baseline_time / effective_thread_improvement)), 6),
                "net_time_change": round(final_time - baseline_time, 6)
            }
        }
    
    def _generate_summary(self, function_profiles: Dict) -> Dict:
        """Generate summary statistics including hybrid analysis"""
        total_simulation_time = sum(data["total_time"] for data in function_profiles.values())
        total_function_calls = sum(data["call_count"] for data in function_profiles.values())
        baseline_total_time = sum(data["hybrid_metrics"]["baseline_time"] for data in function_profiles.values())
        
        # Calculate aggregate effects
        total_time_saved_threading = sum(data["hybrid_metrics"]["time_saved_from_threading"] for data in function_profiles.values())
        total_time_lost_contention = sum(data["hybrid_metrics"]["time_lost_to_contention"] for data in function_profiles.values())
        net_time_change = total_simulation_time - baseline_total_time
        
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
        
        # Categorize functions by net effect
        net_gainers = [(name, data) for name, data in function_profiles.items() 
                      if data["hybrid_metrics"]["net_performance_ratio"] < 1.0]
        net_losers = [(name, data) for name, data in function_profiles.items() 
                     if data["hybrid_metrics"]["net_performance_ratio"] > 1.0]
        
        net_gainers.sort(key=lambda x: x[1]["hybrid_metrics"]["net_time_change"])
        net_losers.sort(key=lambda x: x[1]["hybrid_metrics"]["net_time_change"], reverse=True)
        
        return {
            "total_simulation_time": round(total_simulation_time, 3),
            "baseline_simulation_time": round(baseline_total_time, 3),
            "net_performance_change_percent": round((net_time_change / baseline_total_time) * 100, 1),
            "overall_performance_ratio": round(total_simulation_time / baseline_total_time, 2),
            "total_function_calls": total_function_calls,
            "threading_analysis": {
                "time_saved_from_threading": round(total_time_saved_threading, 3),
                "time_lost_to_contention": round(total_time_lost_contention, 3),
                "net_time_change": round(net_time_change, 3),
                "threading_efficiency_degradation": self.simulation_metadata["system_conditions"]["threading_efficiency_degradation"]
            },
            "top_5_time_consumers": [
                {
                    "function": func_name,
                    "time": func_data["total_time"],
                    "percentage": func_data["percentage_of_total"],
                    "net_effect": func_data["hybrid_metrics"]["net_effect"],
                    "net_change_percent": round((func_data["hybrid_metrics"]["net_performance_ratio"] - 1) * 100, 1)
                }
                for func_name, func_data in sorted_functions[:5]
            ],
            "biggest_net_gainers": [
                {
                    "function": func_name,
                    "time_saved": abs(func_data["hybrid_metrics"]["net_time_change"]),
                    "improvement_percent": round((1 - func_data["hybrid_metrics"]["net_performance_ratio"]) * 100, 1)
                }
                for func_name, func_data in net_gainers[:5]
            ],
            "biggest_net_losers": [
                {
                    "function": func_name,
                    "time_added": func_data["hybrid_metrics"]["net_time_change"],
                    "degradation_percent": round((func_data["hybrid_metrics"]["net_performance_ratio"] - 1) * 100, 1)
                }
                for func_name, func_data in net_losers[:5]
            ]
        }
    
    def save_to_json(self, filename: str = "energyplus_profiling_hybrid.json"):
        """Save hybrid profiling data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.profiling_data, f, indent=2)
        print(f"Hybrid profiling data saved to {filename}")
    
    def print_summary(self):
        """Print a formatted summary of hybrid profiling data"""
        if not self.profiling_data:
            self.generate_profiling_data()
        
        summary = self.profiling_data["summary"]
        metadata = self.profiling_data["metadata"]
        threading = summary["threading_analysis"]
        
        print("\n" + "="*80)
        print("EnergyPlus Performance Profile - MULTITHREADED WITH MEMORY CONTENTION")
        print("="*80)
        print(f"Building Type: {metadata['building_type']}")
        print(f"Climate Zone: {metadata['climate_zone']}")
        print(f"CPU Cores: {metadata['system_conditions']['cpu_cores']}")
        print(f"Thread Pool Size: {metadata['system_conditions']['thread_pool_size']}")
        print(f"Memory Pressure: {metadata['system_conditions']['memory_pressure']}")
        print(f"Available Memory: {metadata['system_conditions']['available_memory']}")
        print(f"Cache Hit Ratio: {metadata['system_conditions']['cache_hit_ratio']}")
        print(f"Threading Efficiency Degradation: {metadata['system_conditions']['threading_efficiency_degradation']}")
        print()
        print(f"Total Simulation Time: {summary['total_simulation_time']:.2f} seconds")
        print(f"Baseline Time (single-threaded, no contention): {summary['baseline_simulation_time']:.2f} seconds")
        print(f"Net Performance Change: {summary['net_performance_change_percent']:+.1f}%")
        print(f"Overall Performance Ratio: {summary['overall_performance_ratio']:.2f}x")
        print()
        print("COMPETING EFFECTS ANALYSIS:")
        print(f"  Time Saved from Threading: {threading['time_saved_from_threading']:.2f} seconds")
        print(f"  Time Lost to Memory Contention: {threading['time_lost_to_contention']:.2f} seconds")
        print(f"  Net Time Change: {threading['net_time_change']:+.2f} seconds")
        
        print(f"\nTop 5 Time-Consuming Functions:")
        print("-" * 75)
        for i, func in enumerate(summary["top_5_time_consumers"], 1):
            effect_symbol = "↑" if func['net_change_percent'] > 0 else "↓" if func['net_change_percent'] < 0 else "="
            print(f"{i}. {func['function']:<35} {func['time']:>8.2f}s ({func['percentage']:>5.1f}%) "
                  f"{effect_symbol} {func['net_change_percent']:+5.1f}% [{func['net_effect']}]")
        
        print(f"\nBiggest Net Gainers (Threading > Contention):")
        print("-" * 60)
        for i, func in enumerate(summary["biggest_net_gainers"], 1):
            print(f"{i}. {func['function']:<35} -{func['time_saved']:>5.2f}s (-{func['improvement_percent']:>5.1f}%)")
        
        print(f"\nBiggest Net Losers (Contention > Threading):")
        print("-" * 60)
        for i, func in enumerate(summary["biggest_net_losers"], 1):
            print(f"{i}. {func['function']:<35} +{func['time_added']:>5.2f}s (+{func['degradation_percent']:>5.1f}%)")
        
        print(f"\nConcurrent Applications:")
        for app in metadata['system_conditions']['concurrent_applications']:
            print(f"  • {app}")


def main():
    """Generate and display EnergyPlus hybrid profiling data"""
    profiler = EnergyPlusHybridProfiler()
    profiler.generate_profiling_data()
    profiler.print_summary()
    profiler.save_to_json()


if __name__ == "__main__":
    main()