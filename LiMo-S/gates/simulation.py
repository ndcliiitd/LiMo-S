import argparse
import os
import importlib
import json
from multiprocessing import Pool
import time
import traceback

class Gate:
    def __init__(self, name, optimization_type):
        self.name = name
        self.optimization_type = optimization_type

    def simulate(self):
        try:
            # Get the absolute path to the gate folder
            gate_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "gates", self.name))

            # Change directory to the gate folder
            os.chdir(gate_folder)

            # Import the user_input module for the respective gate
            module_name = self.name + ".script.user_input"
            #print(module_name)
            user_input = importlib.import_module(module_name)

            # Call the single take_input method to get input values
            input_values = user_input.take_input()

            # Serialize the input values to a JSON file within the 'script' subdirectory
            input_file_path = os.path.join(gate_folder, 'script', 'input.json')
            with open(input_file_path, 'w') as f:
                json.dump(input_values, f)
            print("Creating input.json in directory:", gate_folder)

            # Import the appropriate data_gen module based on the optimization type
            print(self.optimization_type)

            # Construct the module name
            module_name1 = self.name + ".script.data_gen_" + self.optimization_type
            #print(module_name1)
            try:
                data_gen = importlib.import_module(module_name1)
            except ModuleNotFoundError:
                print(f"An error occurred while importing {module_name1}. Make sure the module exists.")

            # Call the simulate method of the data_gen module
            data_gen.simulate()

        except Exception as e:
            print(f"An error occurred while simulating {self.name}: {e}")
            #traceback.print_exc()
        finally:
            #Change back to the parent directory
            os.chdir(original_dir)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Dataset Generation command")
    parser.add_argument('-cell', type=str, help="Gate names for dataset generation (comma-separated)")
    parser.add_argument('-optimize', type=str, default="none", help="Optimization method (none, skew_opt, skew_slew_opt)")
    parser.add_argument('-num_processes', type=int, default=1, help="Number of worker processes to use for multiprocessing")

    args = parser.parse_args()

    # Parse the gate names and optimization method
    gate_names = args.cell.split(',')
    optimization = args.optimize

    # Create a list of Gate objects for the selected gates
    selected_gates = [Gate(name, optimization) for name in gate_names]

    # Get the start time just before creating the worker processes
    start_time = time.time()
    #print("DATASET GENERATION STARTED")
    # Create a pool of worker processes with a maximum of num_processes processes
    with Pool(processes=args.num_processes) as pool:
        # Assign each selected gate to a worker process in the pool
        results = [pool.apply_async(gate.simulate) for gate in selected_gates]

        # Wait for the worker processes to complete
        for result in results:
            result.wait()

    # Get the end time after all worker processes have completed
    end_time = time.time()

    # Calculate the total simulation time (excluding the time spent waiting for worker processes to complete)
    simulation_time = end_time - start_time

    # Display the simulation time
    print(f"\nSimulation time: {simulation_time} seconds")

    # Display a message indicating that all gates have been simulated
    #print("\nAll gates have been simulated!")





