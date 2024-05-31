#import required libraries
import subprocess
import numpy as np
import csv
import re
import os
import csv
import time
import sys
import json

######.............................................................................................................................................######
######.............................................................................................................................................######
#ocean script for the simulation of combinational cell and calculating the value of delays
ocean_script = """

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;SET THE ENVIRONMENT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;Set up the output file
of = outfile(interim_output_file, "w") 

;;Set the simulator to use
simulator(simulator_name)

;;Set the design directory
design(design_dir)

;;Set the results directory
resultsDir(results_dir)

;;Set the stimulus files
stimulusFile(?xlate nil stimulus_file)

;;Write the legend to the output file
fprintf(of," load, slew_d, slew_clk, process, voltage, temperature, skew_d, setup_skew, hold_skew, ckq_delay, D, Q, D_Q_comparision\n")

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;DEFINE FUNCTION USED IN THE SCRIPT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;convert string into floating point number
procedure( StrToNum(arg)
    (float (evalstring arg) )
)

;;Define a function for absolute value
(procedure (absolute x) 
    if( (x >= 1e-15) (x=x) (x=-x) ) 
)

;;if anywhere in dataset generataing the nil convert it into number so that subtarction operation can be performed latter on.
(procedure (conv_nil value)
  (cond ((and (listp value) (null value)) 0)
        ((numberp value) value)
        (t value)
  )
)

;;simulate at the input values and calculate the delay
(procedure (simulation pload pslew_d pslew_clk pcorners pvdd ptemp pskew_d)

    ;;SET THE MODEL FILES AND PROCESS CORNERS
    modelFile( list(model_file pcorners) )

    ;; RUN COMMANDS TO DO TRANSIENT ANALYSIS;;Set the analysis options
    analysis('tran ?param "temp"  ?start  analysis_start  ?stop  analysis_stop  ?step  analysis_step)
    option( 'temp ptemp ) 
    save('all)
    run() 

    ;; DATA ACCESS COMMAND TO PROCESS POST-SIMULATION DATA        
    selectResults('tran)    

    ;; setup_skew
    setup_skew = delay(?wf1 v("/D" ?result "tran") ?value1 0.35 ?edge1 "rising" ?nth1 1 ?td1 0.0 ?tol1 nil ?wf2 v("/CK" ?result "tran") ?value2 0.35 ?edge2 "rising" ?nth2 1 ?tol2 nil ?td2 nil ?stop nil ?multiple nil)

    ;; hold_skew
    hold_skew = delay(?wf1 v("/CK" ?result "tran") ?value1 0.35 ?edge1 "rising" ?nth1 1 ?td1 0.0 ?tol1 nil ?wf2 v("/D" ?result "tran") ?value2 0.35 ?edge2 "falling" ?nth2 1 ?tol2 nil ?td2 nil ?stop nil ?multiple nil)

    ;; ckq_delay
    ckq_delay = delay(?wf1 v("/CK" ?result "tran"), ?value1 0.35, ?edge1 "rising", ?nth1 1, ?td1 0.0, ?tol1 nil, ?wf2 v("/Q" ?result "tran"), ?value2 0.35, ?edge2 "rising", ?nth2 1, ?tol2 nil,  ?td2 nil , ?stop nil, ?multiple nil)

    ;; D value
    D = ymax(v("/D"))

    ;; Q value
    Q = ymax(v("/Q"))

    ;; Compare D and Q
    D_Q_comparision = if( D > Q then "mismatch" else "match")

)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;INPUT PARAMETERS;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; This will create a list for process corners
pcorners_1 = list(pcorners_list)

;; This will create a list for voltage 
pvdd_1 = linRg(StrToNum(pvdd_start) StrToNum(pvdd_stop) StrToNum(pvdd_step)) 

;; This will create a list for temperature
ptemp_1 = linRg(StrToNum(ptemp_start) StrToNum(ptemp_stop) StrToNum(ptemp_step)) 

;;This will create a list for input slew_d , slew_d_1 is passed from the python 
pslew_d_2 = list(StrToNum(pslew_d_1))  

;;This will create a list for input slew_clk, slew_clk_1 is passed from the python 
pslew_clk_2 = list(StrToNum(pslew_clk_1))

;; This will create a list for output capacitance , pload_1 is paased from the python 
pload_2 = list(StrToNum(pload_1)) 

;;This will create a list for input skew 
pskew_d_1 = linRg(StrToNum(pskew_d_start) StrToNum(pskew_d_stop) StrToNum(pskew_d_step))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;RUNNING SIMULATION AND WRITING OUTPUT INTO FILE;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

foreach((pload) pload_2
    desVar("cap", pload)

    foreach( (pslew_d) pslew_d_2
        desVar("slew_d", pslew_d)
     
        foreach( (pslew_clk) pslew_clk_2
            desVar("slew_clk", pslew_clk)

            foreach((pcorners) pcorners_1
                desVar("corners", pcorners)
                     
                foreach( (pvdd) pvdd_1
                    desVar("VDD", pvdd)
                                                 
                    foreach( (ptemp) ptemp_1
                        desVar("temp", ptemp) 
			
			foreach( (pskew_d) pskew_d_1
                            desVar("skew_d", pskew_d)
                                      
                            ;;simulate at the input values and calculate the delay
		            (simulation pload pslew_d pslew_clk pcorners pvdd ptemp pskew_d)

                            ;;if anywhere in dataset generataing the nil convert it into number so that subtarction operation can be performed latter on.
                            (setq setup_skew (conv_nil setup_skew))
                            (setq hold_skew (conv_nil hold_skew))
                            (setq ckq_delay (conv_nil ckq_delay))
                                    
                            ;; write the value in input_file for python and outuput file for ocean script(dataset.csv)                                   
                            newline(of)
                            fprintf( of "%e,%e,%e,%s,%f,%L,%L,%L,%L,%L,%e,%e,%s\n", pload, pslew_d, pslew_clk, pcorners, pvdd, ptemp, pskew_d, setup_skew, hold_skew, ckq_delay, D, Q, D_Q_comparision) 
                      )                               
                   )
               )
           ) 
       )
   )
) 


close(of)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;COMPLETED SCRIPT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

"""

#copied the ocean script into another variable ocean_script_1
ocean_script_1 = ocean_script


######.............................................................................................................................................######
######.............................................................................................................................................######
# Set the working directory to the directory of this script
os.chdir(os.path.dirname(__file__))

# Load the input values from the JSON file
with open('input.json', 'r') as f:
    input_values = json.load(f)

# Extract input values
interim_output_file = "interim/interim_dataset_none.csv"

simulator_name = input_values["simulator_name"]
design_dir = input_values["design_dir"]
results_dir = input_values["results_dir"]
model_file = input_values["model_file"]
stimulus_file = input_values["stimulus_file"]
analysis_start = input_values["analysis_start"]
analysis_stop = input_values["analysis_stop"]
analysis_step = input_values["analysis_step"]
pcorners_list = input_values["pcorners_list"]
pvdd_start = input_values["pvdd_start"]
pvdd_stop = input_values["pvdd_stop"]
pvdd_step = input_values["pvdd_step"]
ptemp_start = input_values["ptemp_start"]
ptemp_stop = input_values["ptemp_stop"]
ptemp_step = input_values["ptemp_step"]
pload_start = input_values["pload_start"]
pload_stop = input_values["pload_stop"]
pload_common_ratio = input_values["pload_common_ratio"]
pslew_d_start = input_values["pslew_d_start"]
pslew_d_stop = input_values["pslew_d_stop"]
pslew_d_common_ratio = input_values["pslew_d_common_ratio"]
pslew_clk_start = input_values["pslew_clk_start"]
pslew_clk_stop = input_values["pslew_clk_stop"]
pslew_clk_common_ratio = input_values["pslew_clk_common_ratio"]
pskew_d_start = input_values["pskew_d_start"]
pskew_d_stop = input_values["pskew_d_stop"]
pskew_d_step = input_values["pskew_d_step"]

output_filename = input_values["output_filename"]

print(output_filename)
def generate_points(start, end, common_ratio):
    
    points = []

    current_point = start
    while current_point <= end:
        points.append(current_point)
        current_point *= common_ratio
    if points[-1] != end:
        points.append(end)
        
    return points

def generate_points2(start, end, common_ratio):
    
    points = []

    current_point = start
    while current_point <= end:
        points.append(current_point)
        current_point *= common_ratio
    
    return points


pload = generate_points2(pload_start, pload_stop, pload_common_ratio)
pslew_d = generate_points2(pslew_d_start, pslew_d_stop, pslew_d_common_ratio)
pslew_clk = generate_points2(pslew_clk_start, pslew_clk_stop, pslew_clk_common_ratio)

# Function to append values from input CSV to output CSV
def append_csv_values(input_file, output_file):
    with open(input_file, 'r', errors='ignore') as input_csv, open(output_file, 'a', newline='') as output_csv:
        reader = csv.reader(input_csv)
        writer = csv.writer(output_csv)
        # Skip the first line of the input CSV
        next(reader, None)
        # Append values from input CSV to output CSV
        for row in reader:
            writer.writerow(row)


#Write the legend to the output file
with open(output_filename, 'w') as f:
    f.write(" load, slew_d, slew_clk, process, voltage, temperature, skew_d, setup_skew, hold_skew, ckq_delay, D, Q, D_Q_comparision\n")


######.............................................................................................................................................######
######.............................................................................................................................................######
# function to replace the placeholders in the ocean script with the values
#The replace() method in Python is used to replace all occurrences of a specified substring with a new substring.In this command, ocean_script is a string variable and replace() is used to replace the substring "pcorners" in ocean_script with the value of corners variable.
def replace_placeholders(ocean_script, output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step,  load_1, slew_d_1, slew_clk_1):
    
    ocean_script = ocean_script.replace("interim_output_file", f'"{interim_output_file}"')
    ocean_script = ocean_script.replace("simulator_name", f'"{simulator_name}"')
    ocean_script = ocean_script.replace("design_dir", f'"{design_dir}"')
    ocean_script = ocean_script.replace("results_dir", f'"{results_dir}"')
    ocean_script = ocean_script.replace("model_file", f'"{model_file}"')
    ocean_script = ocean_script.replace("stimulus_file", f'"{stimulus_file}"')

    ocean_script = ocean_script.replace("analysis_start", f'"{analysis_start}"')
    ocean_script = ocean_script.replace("analysis_stop", f'"{analysis_stop}"')
    ocean_script = ocean_script.replace("analysis_step", f'"{analysis_step}"')

    pcorner_replacement = " ".join([f'"{item}"' for item in pcorners_list])
    ocean_script = ocean_script.replace("pcorners_list", pcorner_replacement)

    ocean_script = ocean_script.replace("pvdd_start", f'"{pvdd_start}"')
    ocean_script = ocean_script.replace("pvdd_stop", f'"{pvdd_stop}"')
    ocean_script = ocean_script.replace("pvdd_step", f'"{pvdd_step}"')

    ocean_script = ocean_script.replace("ptemp_start", f'"{ptemp_start}"')
    ocean_script = ocean_script.replace("ptemp_stop", f'"{ptemp_stop}"')
    ocean_script = ocean_script.replace("ptemp_step", f'"{ptemp_step}"')

    ocean_script = ocean_script.replace("pskew_d_start", f'"{pskew_d_start}"')
    ocean_script = ocean_script.replace("pskew_d_stop", f'"{pskew_d_stop}"')
    ocean_script = ocean_script.replace("pskew_d_step", f'"{pskew_d_step}"')

    #print("Replace the pload in the ocean script with the current load =", load_1)
    ocean_script = ocean_script.replace("pload_1", f'"{(load_1)}"')
    #print("Replace the pslew_a in the ocean script with the current slew_d =", slew_d_1)
    ocean_script = ocean_script.replace("pslew_d_1", f'"{(slew_d_1)}"')
    #print("Replace the pslew_b in the ocean script with the current slew_clk=", slew_clk_1)
    ocean_script = ocean_script.replace("pslew_clk_1", f'"{(slew_clk_1)}"')

    #print("print the current ocean script", ocean_script)
    return ocean_script


######.............................................................................................................................................######
######.............................................................................................................................................######
#Perform the simulation for the given set of input and return the value of setupt_skew, hold_skew, ckq_delay

def simulate(ocean_script, interim_output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step, load_1, slew_d_1, slew_clk_1):
    try:
        ocean_script = replace_placeholders(ocean_script, interim_output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step, load_1, slew_d_1, slew_clk_1)

        # Start a new csh shell in a subproces  
        #print("Number of combination for load and slew (how many time changing enviroment) =", index)                        
        #print("Start a new csh shell in a subprocess \n \n Ocean script running......wait ")
            
        # Run the "ocean" command using C shell and then run ocean script, capture the output
        ocean_script_output = subprocess.run(["csh", "-c", "source /cadence/cshrc; ocean"], input=ocean_script, capture_output=True, text=True)
        # Print the captured output
        print("Standard Output dff:")
        print( ocean_script_output.stdout)

        print("Standard Error dff:")
        print( ocean_script_output.stderr)
    
        #Check if the command was successful or not and print a message accordingly
        if ocean_script_output.returncode == 0:
            print("Ocean environment started successfully dff.")
        else:
            print("Error: Failed to start ocean environment dff")

    except Exception as e:
        print(f"Error during simulation: {e}")

    return ocean_script_output



######.............................................................................................................................................######
######.............................................................................................................................................######
#start to form the dataset
index=0
# Start the overall timer
total_start_time = time.time() 

#print("start for load")
for load_1 in pload:
    #print("start for slew_d")      
    for slew_d_1 in pslew_d:
        #print("start for slew_clk")
        for slew_clk_1 in pslew_clk:
        
            #to see how number of loop run
            index = index+1
            print("DATASET GENERATION STARTED FOR GIVEN INPUT (dff)")
            
            try:
                #Simulate at the input given at a time 
                ocean_script_output = simulate(ocean_script, interim_output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step, load_1, slew_d_1, slew_clk_1)

                # Append values from input CSV to output CSV
                append_csv_values(interim_output_file, output_filename)

                          
                #Replace the values in the ocean script with the variable again")
                ocean_script = ocean_script_1

            except Exception as e:
                print(f"Error during dataset generation: {e}")


######.............................................................................................................................................######
######.............................................................................................................................................######

print("\n**************************************\n")
print("\nDATASET GENERATION COMPLETED dff\n")

# Stop the overall timer
total_end_time = time.time() 
total_elapsed_time = total_end_time - total_start_time
print(f"Total simulation time dff: {total_elapsed_time} seconds")

######.............................................................................................................................................######
######.............................................................................................................................................######



