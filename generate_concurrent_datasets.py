"""
Generate profiling datasets for concurrent EnergyPlus simulations
Creates datasets for different numbers of concurrent simulations with varying thread counts
"""

import json
import random
import math
from datetime import datetime
from pathlib import Path


class ConcurrentSimulationProfiler:
    """Generate profiling data for concurrent EnergyPlus simulations"""
    
    def __init__(self, base_simulation_time=388.23):
        self.base_simulation_time = base_simulation_time
        self.num_threads_per_simulation = [1, 2, 4, 8, 16, 32]
        self.num_concurrent_simulations = [1, 2, 4, 8, 16, 32, 64]
        
        # Base function data (from the original baseline)
        self.base_functions = {
            "SimulateHVAC": {"time": 45.2, "calls": 842, "percentage": 11.64},
            "CalcAirLoopSplitter": {"time": 2.1, "calls": 1147, "percentage": 0.54},
            "SimulateAirLoopComponents": {"time": 18.7, "calls": 952, "percentage": 4.82},
            "CalcFanSystemTemperatures": {"time": 3.4, "calls": 1096, "percentage": 0.88},
            "SimulateCoils": {"time": 8.9, "calls": 992, "percentage": 2.29},
            "CalcCoolingCoil": {"time": 5.2, "calls": 876, "percentage": 1.34},
            "CalcHeatingCoil": {"time": 4.1, "calls": 836, "percentage": 1.06},
            "SimulateChillers": {"time": 12.5, "calls": 426, "percentage": 3.22},
            "CalcBoilerModel": {"time": 6.8, "calls": 364, "percentage": 1.75},
            "SimulatePumps": {"time": 2.9, "calls": 750, "percentage": 0.75},
            "ManageZoneEquipment": {"time": 15.6, "calls": 1200, "percentage": 4.02},
            "CalcZoneAirLoads": {"time": 22.1, "calls": 1172, "percentage": 5.69},
            "SimulateInternalHeatGains": {"time": 7.3, "calls": 1088, "percentage": 1.88},
            "CalcWindowHeatBalance": {"time": 19.8, "calls": 917, "percentage": 5.10},
            "CalcExteriorSurfaceTemp": {"time": 8.7, "calls": 1029, "percentage": 2.24},
            "CalcInteriorSurfaceTemp": {"time": 11.2, "calls": 1049, "percentage": 2.89},
            "CalcHeatBalFiniteDiff": {"time": 31.4, "calls": 733, "percentage": 8.09},
            "CalcHeatBalConductionTransferFunction": {"time": 25.7, "calls": 678, "percentage": 6.62},
            "ManageWeather": {"time": 1.8, "calls": 8728, "percentage": 0.46},
            "CalcSolarRadiation": {"time": 13.5, "calls": 1217, "percentage": 3.48},
            "CalcDifferenceSolarRadiation": {"time": 4.2, "calls": 1076, "percentage": 1.08},
            "InterpolateBetweenTwoValues": {"time": 0.05, "calls": 14799, "percentage": 0.01},
            "CalculateSunDirectionCosines": {"time": 0.8, "calls": 8114, "percentage": 0.21},
            "ManagePlantLoops": {"time": 28.9, "calls": 636, "percentage": 7.44},
            "SimulatePlantProfile": {"time": 3.7, "calls": 693, "percentage": 0.95},
            "UpdatePlantLoopInterface": {"time": 2.1, "calls": 866, "percentage": 0.54},
            "CalcPlantValves": {"time": 1.9, "calls": 427, "percentage": 0.49},
            "CalcTariffEvaluation": {"time": 5.1, "calls": 119, "percentage": 1.31},
            "UpdateUtilityBills": {"time": 2.3, "calls": 142, "percentage": 0.59},
            "EconomicTariffManager": {"time": 3.8, "calls": 104, "percentage": 0.98},
            "UpdateDataandReport": {"time": 12.4, "calls": 186, "percentage": 3.19},
            "WriteOutputToSQLite": {"time": 8.7, "calls": 177, "percentage": 2.24},
            "ReportSurfaceHeatBalance": {"time": 4.6, "calls": 179, "percentage": 1.18},
            "ReportAirHeatBalance": {"time": 3.9, "calls": 178, "percentage": 1.00},
            "UpdateMeterReporting": {"time": 2.1, "calls": 208, "percentage": 0.54},
            "GetInput": {"time": 15.7, "calls": 1, "percentage": 4.04},
            "InitializeSimulation": {"time": 8.3, "calls": 1, "percentage": 2.14},
            "SetupNodeVarsForReporting": {"time": 2.4, "calls": 1, "percentage": 0.62},
            "SetupOutputVariables": {"time": 3.1, "calls": 1, "percentage": 0.80},
            "ValidateInputData": {"time": 4.8, "calls": 1, "percentage": 1.24},
            "PsyRhoAirFnPbTdbW": {"time": 0.02, "calls": 44680, "percentage": 0.01},
            "PsyHFnTdbW": {"time": 0.015, "calls": 49010, "percentage": 0.00},
            "PsyCpAirFnW": {"time": 0.012, "calls": 37769, "percentage": 0.00},
            "PsyTsatFnHPb": {"time": 0.018, "calls": 26732, "percentage": 0.00},
            "POLYF": {"time": 0.008, "calls": 115479, "percentage": 0.00},
            "CurveValue": {"time": 0.012, "calls": 83630, "percentage": 0.00},
            "TableLookup": {"time": 0.025, "calls": 68817, "percentage": 0.01},
            "RegularQn": {"time": 0.035, "calls": 34688, "percentage": 0.01}
        }

    def calculate_performance_factors(self, num_concurrent, threads_per_sim):
        """Calculate performance factors based on concurrency and threading"""
        
        # Resource contention increases with concurrent simulations
        # Memory pressure, I/O contention, cache thrashing
        base_contention = 1.0
        memory_contention = 1.0 + (num_concurrent - 1) * 0.15  # 15% degradation per additional sim
        io_contention = 1.0 + (num_concurrent - 1) * 0.25      # 25% I/O degradation per additional sim
        cache_contention = 1.0 + (num_concurrent - 1) * 0.08   # 8% cache degradation per additional sim
        
        # CPU efficiency - diminishing returns with more threads
        # Single threaded functions don't benefit from threading
        if threads_per_sim == 1:
            cpu_efficiency = 1.0
        else:
            # Amdahl's law approximation - not all code can be parallelized
            parallel_fraction = 0.7  # 70% of code can be parallelized
            cpu_efficiency = 1.0 / (1.0 - parallel_fraction + parallel_fraction / threads_per_sim)
            # Add overhead for thread management
            thread_overhead = 1.0 + (threads_per_sim - 1) * 0.03  # 3% overhead per thread
            cpu_efficiency = cpu_efficiency / thread_overhead
        
        # Context switching penalty increases with total threads
        total_threads = num_concurrent * threads_per_sim
        context_switch_penalty = 1.0 + (total_threads - 1) * 0.002  # 0.2% penalty per thread
        
        return {
            'memory_contention': memory_contention,
            'io_contention': io_contention, 
            'cache_contention': cache_contention,
            'cpu_efficiency': cpu_efficiency,
            'context_switch_penalty': context_switch_penalty,
            'total_threads': total_threads
        }

    def apply_function_specific_effects(self, func_name, base_time, factors):
        """Apply performance effects specific to each function type"""
        
        # Categorize functions by their characteristics
        io_intensive = ['WriteOutputToSQLite', 'UpdateDataandReport', 'GetInput', 'ReportSurfaceHeatBalance', 'ReportAirHeatBalance']
        cpu_intensive = ['CalcHeatBalFiniteDiff', 'CalcHeatBalConductionTransferFunction', 'CalcWindowHeatBalance', 'SimulateHVAC']
        parallelizable = ['CalcZoneAirLoads', 'ManageZoneEquipment', 'SimulateAirLoopComponents', 'CalcSolarRadiation']
        memory_intensive = ['ManagePlantLoops', 'SimulateChillers', 'CalcBoilerModel']
        math_functions = ['POLYF', 'CurveValue', 'TableLookup', 'RegularQn', 'PsyRhoAirFnPbTdbW', 'PsyHFnTdbW']
        
        # Start with base time
        adjusted_time = base_time
        
        # Apply context switching to all functions
        adjusted_time *= factors['context_switch_penalty']
        
        if func_name in io_intensive:
            # I/O functions suffer most from concurrency
            adjusted_time *= factors['io_contention']
            adjusted_time *= factors['memory_contention'] * 0.8  # Some memory impact
            # I/O functions don't benefit much from threading
            if factors['cpu_efficiency'] > 1.0:
                cpu_benefit = 1.0 + (factors['cpu_efficiency'] - 1.0) * 0.1  # Only 10% of CPU benefit
                adjusted_time /= cpu_benefit
        
        elif func_name in cpu_intensive:
            # CPU-intensive functions benefit from threading but suffer from cache contention
            adjusted_time *= factors['cache_contention']
            adjusted_time /= factors['cpu_efficiency']  # Full CPU benefit
            adjusted_time *= factors['memory_contention'] * 0.6  # Moderate memory impact
        
        elif func_name in parallelizable:
            # These functions benefit most from threading
            adjusted_time /= factors['cpu_efficiency'] * 1.1  # 10% extra benefit
            adjusted_time *= factors['cache_contention'] * 0.8  # Less cache impact
            adjusted_time *= factors['memory_contention'] * 0.5  # Lower memory impact
        
        elif func_name in memory_intensive:
            # Memory-intensive functions suffer from memory contention
            adjusted_time *= factors['memory_contention'] * 1.2  # Extra memory impact
            adjusted_time *= factors['cache_contention']
            adjusted_time /= factors['cpu_efficiency'] * 0.8  # Limited CPU benefit
        
        elif func_name in math_functions:
            # Math functions are lightweight, scale well but affected by cache
            adjusted_time *= factors['cache_contention'] * 1.1  # Extra cache sensitivity
            if factors['cpu_efficiency'] > 1.0:
                # Limited benefit due to function call overhead
                cpu_benefit = 1.0 + (factors['cpu_efficiency'] - 1.0) * 0.3
                adjusted_time /= cpu_benefit
        
        else:
            # Default functions - moderate effects
            adjusted_time *= factors['memory_contention'] * 0.7
            adjusted_time *= factors['cache_contention'] * 0.9
            adjusted_time /= factors['cpu_efficiency'] * 0.7
        
        return max(adjusted_time, base_time * 0.1)  # Minimum 10% of original time

    def generate_function_data(self, factors):
        """Generate function timing data with performance effects applied"""
        functions_data = {}
        total_time = 0
        
        for func_name, base_data in self.base_functions.items():
            base_time = base_data["time"]
            base_calls = base_data["calls"]
            
            # Apply performance effects
            adjusted_time = self.apply_function_specific_effects(func_name, base_time, factors)
            
            # Add some realistic variability
            variability = random.uniform(0.95, 1.05)
            final_time = adjusted_time * variability
            
            # Calculate derived metrics
            avg_time_per_call = final_time / base_calls if base_calls > 0 else 0
            min_time = avg_time_per_call * random.uniform(0.1, 0.3)
            max_time = avg_time_per_call * random.uniform(3.0, 8.0)
            std_deviation = avg_time_per_call * random.uniform(0.2, 0.4)
            
            functions_data[func_name] = {
                "total_time": round(final_time, 6),
                "call_count": base_calls,
                "avg_time_per_call": round(avg_time_per_call, 6),
                "min_time": round(min_time, 6),
                "max_time": round(max_time, 6),
                "std_deviation": round(std_deviation, 6),
                "percentage_of_total": 0  # Will be calculated after total is known
            }
            
            total_time += final_time
        
        # Update percentages
        for func_data in functions_data.values():
            func_data["percentage_of_total"] = round((func_data["total_time"] / total_time) * 100, 2)
        
        return functions_data, total_time

    def generate_dataset(self, num_concurrent, threads_per_sim):
        """Generate a complete dataset for given concurrency parameters"""
        
        # Calculate performance factors
        factors = self.calculate_performance_factors(num_concurrent, threads_per_sim)
        
        # Generate function data
        functions_data, total_time = self.generate_function_data(factors)
        
        # Calculate total function calls
        total_calls = sum(func["call_count"] for func in functions_data.values())
        
        # Calculate memory usage estimate (scales with concurrent simulations)
        base_memory_gb = 2.1  # Base memory per simulation
        memory_overhead = 1.0 + (num_concurrent - 1) * 0.3  # 30% overhead per additional sim
        estimated_memory_gb = base_memory_gb * num_concurrent * memory_overhead
        
        # Generate system conditions
        system_conditions = {
            "concurrent_simulations": num_concurrent,
            "threads_per_simulation": threads_per_sim,
            "total_threads": factors['total_threads'],
            "estimated_memory_usage_gb": round(estimated_memory_gb, 1),
            "cpu_utilization_percent": min(95, factors['total_threads'] * 12),
            "scheduler_scenario": self._get_scheduler_scenario(num_concurrent, threads_per_sim),
            "resource_contention_level": self._get_contention_level(factors)
        }
        
        # Create metadata
        metadata = {
            "building_type": "Commercial Office",
            "climate_zone": "4A", 
            "simulation_period": "Annual",
            "timestep": "4 per hour",
            "total_simulation_time": round(total_time, 6),
            "system_conditions": system_conditions,
            "performance_factors": {
                "memory_contention_factor": round(factors['memory_contention'], 3),
                "io_contention_factor": round(factors['io_contention'], 3),
                "cache_contention_factor": round(factors['cache_contention'], 3),
                "cpu_efficiency_factor": round(factors['cpu_efficiency'], 3),
                "context_switch_penalty": round(factors['context_switch_penalty'], 3)
            }
        }
        
        # Create summary statistics
        sorted_functions = sorted(functions_data.items(), key=lambda x: x[1]['total_time'], reverse=True)
        top_5_consumers = []
        for i, (func_name, func_data) in enumerate(sorted_functions[:5]):
            top_5_consumers.append({
                "function": func_name,
                "time": func_data['total_time'],
                "percentage": func_data['percentage_of_total']
            })
        
        most_called = sorted(functions_data.items(), key=lambda x: x[1]['call_count'], reverse=True)[:5]
        most_called_functions = []
        for func_name, func_data in most_called:
            most_called_functions.append({
                "function": func_name,
                "calls": func_data['call_count'],
                "avg_time": func_data['avg_time_per_call']
            })
        
        summary = {
            "total_simulation_time": round(total_time, 3),
            "baseline_simulation_time": self.base_simulation_time,
            "performance_ratio": round(total_time / self.base_simulation_time, 3),
            "total_function_calls": total_calls,
            "concurrent_simulations": num_concurrent,
            "threads_per_simulation": threads_per_sim,
            "total_threads": factors['total_threads'],
            "top_5_time_consumers": top_5_consumers,
            "most_called_functions": most_called_functions
        }
        
        # Create complete dataset
        dataset = {
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "functions": functions_data,
            "summary": summary
        }
        
        return dataset

    def _get_scheduler_scenario(self, num_concurrent, threads_per_sim):
        """Determine scheduler scenario description"""
        total_threads = num_concurrent * threads_per_sim
        
        if total_threads <= 4:
            return "Low contention"
        elif total_threads <= 16:
            return "Moderate contention"
        elif total_threads <= 64:
            return "High contention"
        else:
            return "Severe contention"

    def _get_contention_level(self, factors):
        """Determine overall resource contention level"""
        avg_contention = (factors['memory_contention'] + factors['io_contention'] + 
                         factors['cache_contention'] + factors['context_switch_penalty']) / 4
        
        if avg_contention < 1.2:
            return "Low"
        elif avg_contention < 1.5:
            return "Moderate"
        elif avg_contention < 2.0:
            return "High"
        else:
            return "Severe"

    def generate_all_datasets(self):
        """Generate all concurrent simulation datasets - full matrix"""
        datasets_created = []
        
        print(f"Generating {len(self.num_concurrent_simulations)} × {len(self.num_threads_per_simulation)} = {len(self.num_concurrent_simulations) * len(self.num_threads_per_simulation)} datasets")
        print()
        
        for num_concurrent in self.num_concurrent_simulations:
            for threads_per_sim in self.num_threads_per_simulation:
                print(f"Generating dataset for {num_concurrent} concurrent simulations with {threads_per_sim} threads each...")
                
                dataset = self.generate_dataset(num_concurrent, threads_per_sim)
                
                # Create filename
                filename = f"energyplus_concurrent_{num_concurrent:02d}sims_{threads_per_sim:02d}threads.json"
                
                # Save dataset
                with open(filename, 'w') as f:
                    json.dump(dataset, f, indent=2)
                
                datasets_created.append({
                    'filename': filename,
                    'concurrent_sims': num_concurrent,
                    'threads_per_sim': threads_per_sim,
                    'total_time': dataset['summary']['total_simulation_time'],
                    'performance_ratio': dataset['summary']['performance_ratio']
                })
                
                print(f"✅ Created {filename}")
                print(f"   Total time: {dataset['summary']['total_simulation_time']:.1f}s")
                print(f"   Performance ratio: {dataset['summary']['performance_ratio']:.2f}x")
                print()
        
        return datasets_created


def main():
    """Generate all concurrent simulation datasets"""
    print("🔄 Generating concurrent EnergyPlus simulation datasets...")
    print()
    
    profiler = ConcurrentSimulationProfiler()
    datasets = profiler.generate_all_datasets()
    
    print("📊 Summary of generated datasets:")
    print("-" * 90)
    print(f"{'Filename':<45} {'Sims':<5} {'Threads':<8} {'Time(s)':<8} {'Ratio':<6}")
    print("-" * 90)
    
    # Group by concurrent simulations for better readability
    for num_concurrent in profiler.num_concurrent_simulations:
        concurrent_datasets = [d for d in datasets if d['concurrent_sims'] == num_concurrent]
        if concurrent_datasets:
            print(f"\n{num_concurrent} Concurrent Simulation(s):")
            for dataset_info in concurrent_datasets:
                print(f"  {dataset_info['filename']:<43} "
                      f"{dataset_info['concurrent_sims']:<5} "
                      f"{dataset_info['threads_per_sim']:<8} "
                      f"{dataset_info['total_time']:<8.1f} "
                      f"{dataset_info['performance_ratio']:<6.2f}")
    
    print("-" * 90)
    print(f"✅ Successfully generated {len(datasets)} concurrent simulation datasets")
    print(f"📋 Matrix: {len(profiler.num_concurrent_simulations)} concurrent scenarios × {len(profiler.num_threads_per_simulation)} thread counts = {len(datasets)} total datasets")


if __name__ == "__main__":
    main()