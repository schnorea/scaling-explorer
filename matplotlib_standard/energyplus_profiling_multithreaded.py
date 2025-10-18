"""
Fictional profiling data for EnergyPlus simulation with selective multithreading improvements
Represents timing measurements showing performance gains from parallel execution
of suitable functions in an uncontested environment
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

class EnergyPlusMultithreadedProfiler:
    """
    Simulates profiling data for EnergyPlus with selective multithreading optimizations
    Shows realistic performance improvements for parallelizable functions
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
                "memory_pressure": "Low",
                "available_memory": "14.2GB of 16GB",
                "cache_hit_ratio": "91%",
                "multithreading_strategy": "Selective parallelization",
                "parallel_zones": 12,
                "parallel_surfaces": 24,
                "thread_pool_size": 6
            }
        }
        
    def generate_profiling_data(self) -> Dict:
        """Generate realistic profiling data showing multithreading performance gains"""
        
        # Apply threading improvements based on function characteristics
        # Zone calculations, surface calculations, and HVAC components benefit most
        # Initialization, reporting, and sequential algorithms show little/no improvement
        
        function_profiles = {
            # HVAC System Functions - moderate parallelization potential
            "SimulateHVAC": self._generate_threaded_data(45.2, 12.3, 850, 
                                                        improvement_factor=1.8, thread_efficiency=0.75),
            "CalcAirLoopSplitter": self._generate_threaded_data(2.1, 0.5, 1200,
                                                              improvement_factor=2.2, thread_efficiency=0.85),
            "SimulateAirLoopComponents": self._generate_threaded_data(18.7, 4.2, 950,
                                                                    improvement_factor=2.4, thread_efficiency=0.80),
            "CalcFanSystemTemperatures": self._generate_threaded_data(3.4, 0.8, 1100,
                                                                    improvement_factor=1.9, thread_efficiency=0.70),
            "SimulateCoils": self._generate_threaded_data(8.9, 2.1, 1050,
                                                        improvement_factor=2.1, thread_efficiency=0.78),
            "CalcCoolingCoil": self._generate_threaded_data(5.2, 1.3, 920,
                                                          improvement_factor=2.0, thread_efficiency=0.76),
            "CalcHeatingCoil": self._generate_threaded_data(4.1, 0.9, 880,
                                                          improvement_factor=1.8, thread_efficiency=0.74),
            "SimulateChillers": self._generate_threaded_data(12.5, 3.7, 450,
                                                           improvement_factor=1.6, thread_efficiency=0.65),
            "CalcBoilerModel": self._generate_threaded_data(6.8, 1.8, 380,
                                                          improvement_factor=1.5, thread_efficiency=0.60),
            "SimulatePumps": self._generate_threaded_data(2.9, 0.7, 760,
                                                        improvement_factor=1.4, thread_efficiency=0.55),
            
            # Zone and Surface Functions - highest parallelization potential
            "ManageZoneEquipment": self._generate_threaded_data(15.6, 4.5, 1200,
                                                              improvement_factor=3.2, thread_efficiency=0.90),
            "CalcZoneAirLoads": self._generate_threaded_data(22.1, 6.2, 1150,
                                                           improvement_factor=3.8, thread_efficiency=0.92),
            "SimulateInternalHeatGains": self._generate_threaded_data(7.3, 2.0, 1100,
                                                                    improvement_factor=2.9, thread_efficiency=0.88),
            "CalcWindowHeatBalance": self._generate_threaded_data(19.8, 5.4, 980,
                                                                improvement_factor=4.2, thread_efficiency=0.95),
            "CalcExteriorSurfaceTemp": self._generate_threaded_data(8.7, 2.3, 1050,
                                                                  improvement_factor=3.5, thread_efficiency=0.91),
            "CalcInteriorSurfaceTemp": self._generate_threaded_data(11.2, 3.1, 1020,
                                                                  improvement_factor=3.6, thread_efficiency=0.92),
            
            # Heat Balance - excellent parallelization for surface calculations
            "CalcHeatBalFiniteDiff": self._generate_threaded_data(31.4, 9.8, 720,
                                                                improvement_factor=4.8, thread_efficiency=0.96),
            "CalcHeatBalConductionTransferFunction": self._generate_threaded_data(25.7, 7.1, 680,
                                                                                improvement_factor=4.5, thread_efficiency=0.94),
            
            # Weather and Solar Functions - limited parallelization (sequential nature)
            "ManageWeather": self._generate_threaded_data(1.8, 0.4, 8760,
                                                        improvement_factor=1.1, thread_efficiency=0.30),
            "CalcSolarRadiation": self._generate_threaded_data(13.5, 3.8, 1200,
                                                             improvement_factor=2.8, thread_efficiency=0.85),
            "CalcDifferenceSolarRadiation": self._generate_threaded_data(4.2, 1.1, 1150,
                                                                       improvement_factor=2.6, thread_efficiency=0.83),
            "InterpolateBetweenTwoValues": self._generate_threaded_data(0.05, 0.01, 15600,
                                                                      improvement_factor=1.2, thread_efficiency=0.35),
            "CalculateSunDirectionCosines": self._generate_threaded_data(0.8, 0.2, 8760,
                                                                       improvement_factor=1.3, thread_efficiency=0.40),
            
            # Plant Loop Functions - moderate parallelization (some dependencies)
            "ManagePlantLoops": self._generate_threaded_data(28.9, 8.2, 650,
                                                           improvement_factor=2.2, thread_efficiency=0.75),
            "SimulatePlantProfile": self._generate_threaded_data(3.7, 1.0, 750,
                                                               improvement_factor=1.8, thread_efficiency=0.68),
            "UpdatePlantLoopInterface": self._generate_threaded_data(2.1, 0.6, 890,
                                                                   improvement_factor=1.4, thread_efficiency=0.52),
            "CalcPlantValves": self._generate_threaded_data(1.9, 0.5, 420,
                                                          improvement_factor=1.6, thread_efficiency=0.58),
            
            # Economics and Utility Functions - minimal parallelization
            "CalcTariffEvaluation": self._generate_threaded_data(5.1, 1.4, 120,
                                                               improvement_factor=1.2, thread_efficiency=0.38),
            "UpdateUtilityBills": self._generate_threaded_data(2.3, 0.6, 140,
                                                             improvement_factor=1.1, thread_efficiency=0.32),
            "EconomicTariffManager": self._generate_threaded_data(3.8, 1.0, 110,
                                                                improvement_factor=1.1, thread_efficiency=0.35),
            
            # Output and Reporting Functions - limited parallelization (I/O bound)
            "UpdateDataandReport": self._generate_threaded_data(12.4, 3.5, 200,
                                                              improvement_factor=1.3, thread_efficiency=0.45),
            "WriteOutputToSQLite": self._generate_threaded_data(8.7, 2.2, 180,
                                                              improvement_factor=1.2, thread_efficiency=0.40),
            "ReportSurfaceHeatBalance": self._generate_threaded_data(4.6, 1.2, 195,
                                                                   improvement_factor=1.4, thread_efficiency=0.48),
            "ReportAirHeatBalance": self._generate_threaded_data(3.9, 1.0, 190,
                                                               improvement_factor=1.3, thread_efficiency=0.46),
            "UpdateMeterReporting": self._generate_threaded_data(2.1, 0.5, 210,
                                                               improvement_factor=1.2, thread_efficiency=0.42),
            
            # Initialization and Setup Functions - no parallelization (run once, sequential)
            "GetInput": self._generate_threaded_data(15.7, 0.0, 1,
                                                   improvement_factor=1.0, thread_efficiency=0.0),
            "InitializeSimulation": self._generate_threaded_data(8.3, 0.0, 1,
                                                               improvement_factor=1.0, thread_efficiency=0.0),
            "SetupNodeVarsForReporting": self._generate_threaded_data(2.4, 0.0, 1,
                                                                    improvement_factor=1.0, thread_efficiency=0.0),
            "SetupOutputVariables": self._generate_threaded_data(3.1, 0.0, 1,
                                                               improvement_factor=1.0, thread_efficiency=0.0),
            "ValidateInputData": self._generate_threaded_data(4.8, 0.0, 1,
                                                            improvement_factor=1.0, thread_efficiency=0.0),
            
            # Psychrometric Functions - excellent vectorization/SIMD potential
            "PsyRhoAirFnPbTdbW": self._generate_threaded_data(0.02, 0.005, 45000,
                                                            improvement_factor=2.8, thread_efficiency=0.85),
            "PsyHFnTdbW": self._generate_threaded_data(0.015, 0.003, 52000,
                                                     improvement_factor=2.9, thread_efficiency=0.87),
            "PsyCpAirFnW": self._generate_threaded_data(0.012, 0.002, 38000,
                                                      improvement_factor=2.7, thread_efficiency=0.84),
            "PsyTsatFnHPb": self._generate_threaded_data(0.018, 0.004, 28000,
                                                       improvement_factor=2.6, thread_efficiency=0.82),
            
            # Mathematical Utility Functions - excellent vectorization potential
            "POLYF": self._generate_threaded_data(0.008, 0.001, 125000,
                                                improvement_factor=3.2, thread_efficiency=0.90),
            "CurveValue": self._generate_threaded_data(0.012, 0.002, 89000,
                                                     improvement_factor=3.0, thread_efficiency=0.88),
            "TableLookup": self._generate_threaded_data(0.025, 0.005, 67000,
                                                      improvement_factor=2.4, thread_efficiency=0.78),
            "RegularQn": self._generate_threaded_data(0.035, 0.008, 34000,
                                                    improvement_factor=2.2, thread_efficiency=0.75),
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
    
    def _generate_threaded_data(self, baseline_time: float, baseline_std: float, 
                              call_count: int, improvement_factor: float, 
                              thread_efficiency: float) -> Dict:
        """Generate function timing data with multithreading improvements"""
        
        # Calculate improved execution time
        # improvement_factor is the theoretical speedup, thread_efficiency accounts for overhead
        actual_improvement = 1 + (improvement_factor - 1) * thread_efficiency
        improved_time = baseline_time / actual_improvement
        
        # Reduce variability slightly due to more consistent parallel execution
        improved_std = baseline_std * 0.85
        
        # Call counts remain the same
        actual_calls = max(1, int(call_count * random.uniform(0.98, 1.02)))
        
        # Generate individual call times with lower variability
        if actual_calls > 0:
            avg_per_call = improved_time / actual_calls
            std_per_call = improved_std / actual_calls if actual_calls > 1 else 0
            
            call_times = []
            for _ in range(min(100, actual_calls)):
                call_time = max(0.001, random.normalvariate(avg_per_call, std_per_call))
                call_times.append(call_time)
        else:
            call_times = []
        
        # Add small random variation to total time
        total_time = improved_time + random.normalvariate(0, improved_std * 0.1)
        total_time = max(0.001, total_time)
        
        avg_per_call = total_time / actual_calls if actual_calls > 0 else total_time
        
        return {
            "total_time": round(total_time, 6),
            "call_count": actual_calls,
            "avg_time_per_call": round(avg_per_call, 6),
            "min_time": round(min(call_times) if call_times else avg_per_call, 6),
            "max_time": round(max(call_times) if call_times else avg_per_call, 6),
            "std_deviation": round(improved_std / actual_calls if actual_calls > 1 else 0, 6),
            "percentage_of_total": 0.0,  # Will be calculated in summary
            "threading_metrics": {
                "baseline_time": round(baseline_time, 6),
                "improvement_factor": round(improvement_factor, 2),
                "thread_efficiency": round(thread_efficiency, 2),
                "actual_speedup": round(actual_improvement, 2),
                "performance_improvement_percent": round((actual_improvement - 1) * 100, 1),
                "time_saved": round(baseline_time - total_time, 6)
            }
        }
    
    def _generate_summary(self, function_profiles: Dict) -> Dict:
        """Generate summary statistics including threading analysis"""
        total_simulation_time = sum(data["total_time"] for data in function_profiles.values())
        total_function_calls = sum(data["call_count"] for data in function_profiles.values())
        baseline_total_time = sum(data["threading_metrics"]["baseline_time"] for data in function_profiles.values())
        
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
        
        # Calculate threading impact metrics
        overall_improvement = ((baseline_total_time - total_simulation_time) / baseline_total_time) * 100
        
        # Find most improved functions
        most_improved = sorted(
            function_profiles.items(),
            key=lambda x: x[1]["threading_metrics"]["time_saved"],
            reverse=True
        )
        
        return {
            "total_simulation_time": round(total_simulation_time, 3),
            "baseline_simulation_time": round(baseline_total_time, 3),
            "overall_performance_improvement_percent": round(overall_improvement, 1),
            "time_saved_through_threading": round(baseline_total_time - total_simulation_time, 3),
            "overall_speedup_factor": round(baseline_total_time / total_simulation_time, 2),
            "total_function_calls": total_function_calls,
            "top_5_time_consumers": [
                {
                    "function": func_name,
                    "time": func_data["total_time"],
                    "percentage": func_data["percentage_of_total"],
                    "improvement_percent": func_data["threading_metrics"]["performance_improvement_percent"]
                }
                for func_name, func_data in sorted_functions[:5]
            ],
            "most_improved_by_threading": [
                {
                    "function": func_name,
                    "time_saved": func_data["threading_metrics"]["time_saved"],
                    "speedup_factor": func_data["threading_metrics"]["actual_speedup"],
                    "improvement_percent": func_data["threading_metrics"]["performance_improvement_percent"]
                }
                for func_name, func_data in most_improved[:5]
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
    
    def save_to_json(self, filename: str = "energyplus_profiling_multithreaded.json"):
        """Save multithreaded profiling data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.profiling_data, f, indent=2)
        print(f"Multithreaded profiling data saved to {filename}")
    
    def print_summary(self):
        """Print a formatted summary of multithreaded profiling data"""
        if not self.profiling_data:
            self.generate_profiling_data()
        
        summary = self.profiling_data["summary"]
        metadata = self.profiling_data["metadata"]
        
        print("\n" + "="*70)
        print("EnergyPlus Simulation Performance Profile - MULTITHREADED")
        print("="*70)
        print(f"Building Type: {metadata['building_type']}")
        print(f"Climate Zone: {metadata['climate_zone']}")
        print(f"CPU Cores: {metadata['system_conditions']['cpu_cores']}")
        print(f"Thread Pool Size: {metadata['system_conditions']['thread_pool_size']}")
        print(f"Available Memory: {metadata['system_conditions']['available_memory']}")
        print(f"Cache Hit Ratio: {metadata['system_conditions']['cache_hit_ratio']}")
        print()
        print(f"Total Simulation Time: {summary['total_simulation_time']:.2f} seconds")
        print(f"Baseline Time (single-threaded): {summary['baseline_simulation_time']:.2f} seconds")
        print(f"Performance Improvement: {summary['overall_performance_improvement_percent']:.1f}%")
        print(f"Overall Speedup Factor: {summary['overall_speedup_factor']:.2f}x")
        print(f"Time Saved Through Threading: {summary['time_saved_through_threading']:.2f} seconds")
        print(f"Total Function Calls: {summary['total_function_calls']:,}")
        
        print(f"\nTop 5 Time-Consuming Functions (with improvements):")
        print("-" * 65)
        for i, func in enumerate(summary["top_5_time_consumers"], 1):
            print(f"{i}. {func['function']:<35} {func['time']:>8.2f}s ({func['percentage']:>5.1f}%) "
                  f"[+{func['improvement_percent']:>5.1f}%]")
        
        print(f"\nMost Improved by Multithreading:")
        print("-" * 55)
        for i, func in enumerate(summary["most_improved_by_threading"], 1):
            print(f"{i}. {func['function']:<35} -{func['time_saved']:>5.2f}s "
                  f"({func['speedup_factor']:>4.1f}x speedup)")


def main():
    """Generate and display EnergyPlus multithreaded profiling data"""
    profiler = EnergyPlusMultithreadedProfiler()
    profiler.generate_profiling_data()
    profiler.print_summary()
    profiler.save_to_json()


if __name__ == "__main__":
    main()