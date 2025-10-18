"""
Fictional profiling data for EnergyPlus simulation application
Represents timing measurements for various functions in a building energy simulation
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple

class EnergyPlusProfiler:
    """
    Simulates profiling data for EnergyPlus building energy simulation
    """
    
    def __init__(self):
        self.profiling_data = {}
        self.simulation_metadata = {
            "building_type": "Commercial Office",
            "climate_zone": "4A",
            "simulation_period": "Annual",
            "timestep": "4 per hour",
            "total_simulation_time": 0.0
        }
        
    def generate_profiling_data(self) -> Dict:
        """Generate realistic profiling data for EnergyPlus functions"""
        
        # Core simulation functions and their typical execution times (in seconds)
        function_profiles = {
            # HVAC System Functions
            "SimulateHVAC": self._generate_function_data(45.2, 12.3, 850),
            "CalcAirLoopSplitter": self._generate_function_data(2.1, 0.5, 1200),
            "SimulateAirLoopComponents": self._generate_function_data(18.7, 4.2, 950),
            "CalcFanSystemTemperatures": self._generate_function_data(3.4, 0.8, 1100),
            "SimulateCoils": self._generate_function_data(8.9, 2.1, 1050),
            "CalcCoolingCoil": self._generate_function_data(5.2, 1.3, 920),
            "CalcHeatingCoil": self._generate_function_data(4.1, 0.9, 880),
            "SimulateChillers": self._generate_function_data(12.5, 3.7, 450),
            "CalcBoilerModel": self._generate_function_data(6.8, 1.8, 380),
            "SimulatePumps": self._generate_function_data(2.9, 0.7, 760),
            
            # Zone and Surface Functions
            "ManageZoneEquipment": self._generate_function_data(15.6, 4.5, 1200),
            "CalcZoneAirLoads": self._generate_function_data(22.1, 6.2, 1150),
            "SimulateInternalHeatGains": self._generate_function_data(7.3, 2.0, 1100),
            "CalcWindowHeatBalance": self._generate_function_data(19.8, 5.4, 980),
            "CalcExteriorSurfaceTemp": self._generate_function_data(8.7, 2.3, 1050),
            "CalcInteriorSurfaceTemp": self._generate_function_data(11.2, 3.1, 1020),
            "CalcHeatBalFiniteDiff": self._generate_function_data(31.4, 9.8, 720),
            "CalcHeatBalConductionTransferFunction": self._generate_function_data(25.7, 7.1, 680),
            
            # Weather and Solar Functions
            "ManageWeather": self._generate_function_data(1.8, 0.4, 8760),
            "CalcSolarRadiation": self._generate_function_data(13.5, 3.8, 1200),
            "CalcDifferenceSolarRadiation": self._generate_function_data(4.2, 1.1, 1150),
            "InterpolateBetweenTwoValues": self._generate_function_data(0.05, 0.01, 15600),
            "CalculateSunDirectionCosines": self._generate_function_data(0.8, 0.2, 8760),
            
            # Plant Loop Functions
            "ManagePlantLoops": self._generate_function_data(28.9, 8.2, 650),
            "SimulatePlantProfile": self._generate_function_data(3.7, 1.0, 750),
            "UpdatePlantLoopInterface": self._generate_function_data(2.1, 0.6, 890),
            "CalcPlantValves": self._generate_function_data(1.9, 0.5, 420),
            
            # Economics and Utility Functions
            "CalcTariffEvaluation": self._generate_function_data(5.1, 1.4, 120),
            "UpdateUtilityBills": self._generate_function_data(2.3, 0.6, 140),
            "EconomicTariffManager": self._generate_function_data(3.8, 1.0, 110),
            
            # Output and Reporting Functions
            "UpdateDataandReport": self._generate_function_data(12.4, 3.5, 200),
            "WriteOutputToSQLite": self._generate_function_data(8.7, 2.2, 180),
            "ReportSurfaceHeatBalance": self._generate_function_data(4.6, 1.2, 195),
            "ReportAirHeatBalance": self._generate_function_data(3.9, 1.0, 190),
            "UpdateMeterReporting": self._generate_function_data(2.1, 0.5, 210),
            
            # Initialization and Setup Functions
            "GetInput": self._generate_function_data(15.7, 0.0, 1),
            "InitializeSimulation": self._generate_function_data(8.3, 0.0, 1),
            "SetupNodeVarsForReporting": self._generate_function_data(2.4, 0.0, 1), 
            "SetupOutputVariables": self._generate_function_data(3.1, 0.0, 1),
            "ValidateInputData": self._generate_function_data(4.8, 0.0, 1),
            
            # Psychrometric Functions
            "PsyRhoAirFnPbTdbW": self._generate_function_data(0.02, 0.005, 45000),
            "PsyHFnTdbW": self._generate_function_data(0.015, 0.003, 52000),
            "PsyCpAirFnW": self._generate_function_data(0.012, 0.002, 38000),
            "PsyTsatFnHPb": self._generate_function_data(0.018, 0.004, 28000),
            
            # Mathematical Utility Functions
            "POLYF": self._generate_function_data(0.008, 0.001, 125000),
            "CurveValue": self._generate_function_data(0.012, 0.002, 89000),
            "TableLookup": self._generate_function_data(0.025, 0.005, 67000),
            "RegularQn": self._generate_function_data(0.035, 0.008, 34000),
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
    
    def _generate_function_data(self, avg_time: float, std_dev: float, call_count: int) -> Dict:
        """Generate realistic function timing data"""
        # Add some variability to call counts
        actual_calls = max(1, int(call_count * random.uniform(0.95, 1.05)))  # Ensure at least 1 call
        
        # Generate individual call times with normal distribution
        if actual_calls > 0:
            avg_per_call = avg_time / actual_calls
            std_per_call = std_dev / actual_calls if actual_calls > 1 else 0
            call_times = [max(0.001, random.normalvariate(avg_per_call, std_per_call)) 
                         for _ in range(min(100, actual_calls))]  # Sample for large call counts
        else:
            call_times = []
        
        total_time = avg_time + random.normalvariate(0, std_dev * 0.1)
        total_time = max(0.001, total_time)  # Ensure positive time
        
        avg_per_call = total_time / actual_calls if actual_calls > 0 else total_time
        
        return {
            "total_time": round(total_time, 6),
            "call_count": actual_calls,
            "avg_time_per_call": round(avg_per_call, 6),
            "min_time": round(min(call_times) if call_times else avg_per_call, 6),
            "max_time": round(max(call_times) if call_times else avg_per_call, 6),
            "std_deviation": round(std_dev / actual_calls if actual_calls > 1 else 0, 6),
            "percentage_of_total": 0.0  # Will be calculated in summary
        }
    
    def _generate_summary(self, function_profiles: Dict) -> Dict:
        """Generate summary statistics"""
        total_simulation_time = sum(data["total_time"] for data in function_profiles.values())
        total_function_calls = sum(data["call_count"] for data in function_profiles.values())
        
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
        
        return {
            "total_simulation_time": round(total_simulation_time, 3),
            "total_function_calls": total_function_calls,
            "top_5_time_consumers": [
                {
                    "function": func_name,
                    "time": func_data["total_time"],
                    "percentage": func_data["percentage_of_total"]
                }
                for func_name, func_data in sorted_functions[:5]
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
    
    def save_to_json(self, filename: str = "energyplus_profiling_data.json"):
        """Save profiling data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.profiling_data, f, indent=2)
        print(f"Profiling data saved to {filename}")
    
    def print_summary(self):
        """Print a formatted summary of profiling data"""
        if not self.profiling_data:
            self.generate_profiling_data()
        
        summary = self.profiling_data["summary"]
        print("\n" + "="*60)
        print("EnergyPlus Simulation Performance Profile")
        print("="*60)
        print(f"Building Type: {self.simulation_metadata['building_type']}")
        print(f"Climate Zone: {self.simulation_metadata['climate_zone']}")
        print(f"Total Simulation Time: {summary['total_simulation_time']:.2f} seconds")
        print(f"Total Function Calls: {summary['total_function_calls']:,}")
        
        print(f"\nTop 5 Time-Consuming Functions:")
        print("-" * 50)
        for i, func in enumerate(summary["top_5_time_consumers"], 1):
            print(f"{i}. {func['function']:<35} {func['time']:>8.2f}s ({func['percentage']:>5.1f}%)")
        
        print(f"\nMost Called Functions:")
        print("-" * 50)
        for i, func in enumerate(summary["most_called_functions"], 1):
            print(f"{i}. {func['function']:<35} {func['calls']:>8,} calls (avg: {func['avg_time']:>6.4f}s)")


def main():
    """Generate and display EnergyPlus profiling data"""
    profiler = EnergyPlusProfiler()
    profiler.generate_profiling_data()
    profiler.print_summary()
    profiler.save_to_json()


if __name__ == "__main__":
    main()