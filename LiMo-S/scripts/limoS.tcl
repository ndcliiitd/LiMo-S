#!/usr/bin/env tclsh

# Function to display the welcome message and instructions
proc display_welcome_message {} {
    puts "-------------------------------------------------"
    puts "Welcome to LiMo-S!"
    puts ""
    puts "LiMo-S - An Intelligent Library Model"
    puts ""
    puts "LiMo-S is a tool for creating Intelligent Library Models for sequential standard cells. "
    puts "It enables the generation of datasets used to train the models, which in turn helps perform a more accurate timing analysis and build a robust signoff framework."
    puts ""
    puts "Type 'help' for a list of available commands."
    puts "Type 'exit' to exit the tool."
    puts "-------------------------------------------------"
    puts ""
}

# Function to display the list of available command
proc display_available_commands {} {
    puts "Available commands:"
    puts "1. help: Shows available commands."
    puts "2. getLibCells: Lists available sequential cells in the directory \$lm_gate_dir."
    puts "3. getVar VAR_NAME: Reports the current value of the tool variable VAR_NAME."
    puts "4. setVar VAR_NAME Value: Sets the given <Value> to the tool variable VAR_NAME."
    puts "5. makeOutput: Create empty folders in output directory with the same name as the  gates in the gates directory."
    puts "6. setInput -cell CELLNAME: Opens user_input.py file for a specified sequential cell using gedit for reading/editing."
    puts "7. genDataset -cell CELLNAME -num_processes NUM_OF_CORES: Initiates dataset generation for selected sequential cells with an option including multiprocessing. e.g usage : genDataset -cell DFFQX1 DFFQX2 -num_processes 2."
    puts "8. viewDataset -cell CELLNAME file_name FILENAME: Opens the FILENAME file for a specific sequential cell using the default CSV viewer. "
    puts "9. loadData -cell CELLNAME -file_name FILENAME: Loads the FILENAME file for a specific sequential cell using the default CSV viewer."
    puts "10. plotData -cell CELLNAME -file_name FILENAME: Generates plot to visualize the dataset."
    puts "11. infoData -cell CELLNAME -file_name FILENAME: Displays and saves data for the specified sequential cell"
    puts "12. splitData -cell CELLNAME -file_name FILENAME -test_size TESTSIZE: Split the data of the FILENAME and saves it in a temporary directory for the specifed sequential cell"
    puts "13. preProcessData_train -cell CELLNAME: Preprocesses data for training for the specifed sequential cell."
    puts "14. preProcessData_test -cell CELLNAME: Preprocesses data for testing for the specifed sequential cell."
    puts "16. trainModel -cell CELLNAME -output MODELNAME: Train a machine learning model for the specifed sequential cell and save the trained model."
    puts "16. testModel -cell CELLNAME -load MODELNAME -report REPORTNAME: Tests a machine learning model for a sequential cell and generates a report."
    puts "17. exit: Exit the tool LiMo-S."
}

# Function to list available digital logic gates
proc list_gates {gates_directory} {
    set available_gates [glob -directory $gates_directory -type d -tails -nocomplain *]
    set gate_count 0
    set gate_names [join $available_gates ","]

    puts "Available Logic Gates : $gate_names"
    puts "Total number of gates in lm_gate_dir: [llength $available_gates]"
}

proc make_output_folder {gates_directory output_directory} {
    set available_gates [glob -directory $gates_directory -type d -tails -nocomplain *]
    set gate_count 0
    set gate_names [join $available_gates ","]

    puts "Available Logic Gates: $gate_names"
    puts "Total number of gates in lm_gate_dir: [llength $available_gates]"

    foreach gate $available_gates {
        set gate_output_directory [file join $output_directory $gate]

        # Check if the output directory for the gate exists, if not, create it
        if {![file isdirectory $gate_output_directory]} {
            file mkdir $gate_output_directory
            puts "Created empty output directory for $gate: $gate_output_directory"
        } else {
            puts "Output directory for $gate already exists: $gate_output_directory"
        }
    }
}


# Function to open the user_input.py file for a specific sequential cell using the default text editor
proc open_user_input {gate_name gates_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set user_input_file [file join $gate_folder "script" "user_input.py"]

    if {[file exists $user_input_file]} {
        exec gedit $user_input_file &
    } else {
        puts "user_input.py file does not exist for gate: $gate_name"
    }
}

proc gen_dataset {args} {
    # Default values
    set gate_names {}
    set num_processes 1

    # Initialize a list to store the command parts
    set command_parts [list]
    # Process the arguments
    set gate_specified 0
    set gate_names_specified 0
    set skip_next_arg 0
    foreach arg $args {
        if {$skip_next_arg} {
            set skip_next_arg 0
            continue
        }
        switch -- $arg {
            "-cell" {
                # The next argument(s) should be gate names, so add them to the gate_names list
                set gate_specified 1
                set gate_names_specified 1
            }
            "-num_processes" {
                set num_processes [lindex $args [expr [lsearch $args $arg] + 1]]
                set skip_next_arg 1
            }
            default {
                if {$gate_names_specified} {
                    lappend gate_names $arg
                }
            }
        }
    }

    # Check if gate names are specified
    if {$gate_specified == 0 || [llength $gate_names] == 0} {
        puts "Usage: genDataset -cell CELLNAME [CELLNAME...]  -num_processes NUM"
        return
    }

    # Construct the Python command to run the script
    set python_executable "~/miniconda3/bin/python3"

    set gates_path "../gates"
    set gates_directory [file normalize [file join [file dirname [info script]] $gates_path]]
    set python_script [file join $gates_directory "simulation.py"]

    puts "DATASET GENERATION STARTED...........WAIT"
    # Run the Python script using the exec command
    if {[catch {exec $python_executable $python_script -cell [join $gate_names ,] -num_processes $num_processes} result]} {
        puts "An error occurred while executing the Python script $python_script:\n$result"
    } else {
        puts $result
        puts "DATASET GENERATION COMPLETED (ignore error:simulate() missing 13 required positional arguments)"
    }
}

#genDataset -cell NAND2X1_7nm -num_processes 1

# Function to open the dataset file for a specific sequential cell
proc view_dataset {gate_name file_name output_directory} {
    set gate_folder [file join $output_directory $gate_name]
    set dataset_file [file join $gate_folder $file_name]
    puts $dataset_file
    if {[file exists $dataset_file]} {
        # Check if gio is available on your system
        set gio_available [catch {exec gio open $dataset_file &} result]

        if {$gio_available == 0} {
            # Use gio open to open the specified file in the background
            exec gio open $dataset_file &

            # Immediately return without waiting
            return
        } else {
            # If gio is not available, use xdg-open as a fallback
            exec xdg-open $dataset_file &

            # Immediately return without waiting
            return
        }
    } else {
        puts "Dataset file does not exist for gate: $gate_name"
    }
}

#viewDataset -cell nand2x1 -file_name GPr3_main_dataset_nand2x1.csv


# Function to load data for a specific sequential cell
proc load_data {gate_name file_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set dataset_file [file join $output_directory $gate_name $file_name]

    if {[file exists $dataset_file]} {
        # Pass the path of the dataset file to loadData.py
        set command [exec python [file join $gate_folder "script" "loadData.py"] $dataset_file]

        if {$command ne ""} {
            puts $command
        } else {
            puts "No data returned from the loadData script for gate: $gate_name"
        }
    } else {
        puts "Dataset file does not exist for gate: $gate_name"
    }
}

#loadData -cell nand2x1 -file_name GPr3_main_dataset_nand2x1.csv

# Function to visualize and save data using plotData
proc plot_data {gate_name file_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set plot_data_script [file join $gate_folder "script" "plotData.py"]
    set file_path [file join $output_directory $gate_name $file_name]
    
    if {[file exists $plot_data_script]} {
        if {$file_name eq ""} {
            # Use the default file name in the plotData.py script
            set command [exec python $plot_data_script $file_path $output_directory $gate_name]
        } else {
            # Use the provided file name
            set command [exec python $plot_data_script $file_path $output_directory $gate_name]
        }
        
        if {$command ne ""} {
            puts $command
        } else {
            puts "No data returned from the plotData script for gate: $gate_name"
        }
    } else {
        puts "plotData script does not exist for gate: $gate_name"
    }
}

#plotData -cell DFFQX1 -file_name GPr3_main_dataset_DFFQX1.csv

# Function to info data for a specific sequential cell
proc info_data {gate_name file_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set info_data_script [file join $gate_folder "script" "infoData.py"]
    set file_path [file join $output_directory $gate_name $file_name]
    
    if {[file exists $info_data_script]} {
        if {$file_name eq ""} {
            # Use the default file name in the infoData.py script
            set command [exec python $info_data_script $file_path $output_directory $gate_name]
        } else {
            # Use the provided file name
            set command [exec python $info_data_script $file_path $output_directory $gate_name]
        }
        
        if {$command ne ""} {
            puts $command
        } else {
            puts "No data returned from the infoData script for gate: $gate_name"
        }
    } else {
        puts "infoData script does not exist for gate: $gate_name"
    }
}

#infoData -cell nand2x1 -file_name GPr3_main_dataset_nand2x1.csv

# Function to split data using splitData.py
proc split_data {gate_name file_name test_size gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set split_data_script [file join $gate_folder "script" "splitData.py"]
    set file_path [file join $output_directory $gate_name $file_name]
    
    if {[file exists $split_data_script]} {
        if {$file_name eq ""} {
            # Use the default file name in the infoData.py script
            set command [exec python $split_data_script $file_path $test_size $output_directory $gate_name]
        } else {
            # Use the provided file name
            set command [exec python $split_data_script $file_path $test_size $output_directory $gate_name]
        }
        
        if {$command ne ""} {
            puts $command
        } else {
            puts "No data returned from the splitData script for gate: $gate_name"
        }
    } else {
        puts "splitData script does not exist for gate: $gate_name"
    }
}

#splitData -cell nand2x1 -file_name GPr3_main_dataset_nand2x1.csv -test_size 0.2

# Function to run preProcessData_train.py for a specific sequential cell
proc preProcessData_train {gate_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set preprocess_data_train_script [file join $gate_folder "script" "preProcessData_train.py"]

    if {[file exists $preprocess_data_train_script]} {
        # Build the command to run preProcessData_train.py
        set command [exec python $preprocess_data_train_script $gate_name $output_directory]
        puts "preprocessed_X_train, preprocessed_Y_train is generated in $output_directory/$gate_name"
        if {$command ne ""} {
            puts $command            
        } 
    } else {
        puts "preProcessData_train.py file does not exist for gate: $gate_name"
    }
}
#preProcessData_train -cell nand2x1
#preProcessData_test -cell nand2x1

# Function to run preProcessData_test.py for a specific sequential cell
proc preProcessData_test {gate_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set preprocess_data_test_script [file join $gate_folder "script" "preProcessData_test.py"]

    if {[file exists $preprocess_data_test_script]} {
        # Build the command to run preProcessData_train.py
        set command [exec python $preprocess_data_test_script $gate_name $output_directory]
        puts "preprocessed_X_test, preprocessed_Y_test is generated in $output_directory/$gate_name"
        if {$command ne ""} {
            puts $command            
        } 
    } else {
        puts "preProcessData_test.py file does not exist for gate: $gate_name"
    }
}

# Function to train the model for a specific sequential cell and save it
proc train_model {gate_name model_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set train_model_script [file join $gate_folder "script" "trainModel.py"]
    
    if {[file exists $train_model_script]} {
        if {$model_name eq ""} {
            # Use the default model name in the trainModel.py script
            set command [exec python $train_model_script $gate_name $output_directory]
        } else {
            # Use the provided model name
            set command [exec python $train_model_script $gate_name $model_name $output_directory]
            puts "Trained model is generated in $output_directory/$gate_name" 
        }
        
        if {$command ne ""} {
            puts $command
        } else {
            puts "No data returned from the trainModel script for gate: $gate_name"
        }
    } else {
        puts "trainModel.py file does not exist for gate: $gate_name"
    }
}

#trainModel -cell nand2x1 -output trained_model_nand2x1

# Function to test the model for a specific sequential cell and save the report
proc test_model {gate_name model_name report_name gates_directory output_directory} {
    set gate_folder [file join $gates_directory $gate_name]
    set test_model_script [file join $gate_folder "script" "testModel.py"]
    
    if {[file exists $test_model_script]} {
        if {$model_name eq ""} {
            puts "Missing model name. Provide a model name to test."
        } else {
            set command [exec python $test_model_script $gate_name  $model_name $report_name $output_directory]
            puts "Reports is generated in $output_directory/$gate_name"
            if {$command ne ""} {
                puts $command
            } else {
                puts "No data returned from the testModel script for gate: $gate_name"
            }
        }
    } else {
        puts "testModel.py file does not exist for gate: $gate_name"
    }
}

#testModel -cell nand2x1 -load trained_model_nand2x1.pkl -report report_nand2x1.txt

proc valid_variables {} {
		    puts "Valid variable names:"
		    puts "    lm_gate_dir"
		    puts "    lm_out_dir"
}

# Execute the LiMo-S tool
proc execute_LiMo-S_tool {} {

    set gates_path "../gates"
    set gates_directory [file normalize [file join [file dirname [info script]] $gates_path]]
    #set output_directory $gates_directory
    set output_directory [file join [file dirname $gates_directory] "output"]
    
    #set gates_directory "/home/poojabe/Desktop/PhD_Research/src_project/ml_lib_char/LiMo-S/gates"
    set python_executable "python3" ;# Update with the correct Python executable path
    # Display the welcome message
    display_welcome_message
    #puts "Make sure that the gates folder is located in this location: $gates_directory"
    # Open a shell-like interactive environment
    puts "Launching LiMo-S shell."
    puts ""
    
    while {1} {
        puts -nonewline ">> "
        flush stdout
        set user_input [gets stdin]
        
        # Remove leading and trailing spaces from user input
        set user_input [string trim $user_input]
        # Split user input into command and arguments using hyphens
        set parts [split $user_input]
        set command [lindex $parts 0]
        
        
        # Process user input
        switch -glob -- $command {
	    "setVar" {
                if {[llength $parts] == 3} {
			set var_name [lindex $parts 1]
			set var_val [lindex $parts 2]
			if {$var_name eq "lm_gate_dir"} {
                    		set gates_directory $var_val
			} elseif  {$var_name eq  "lm_out_dir"} {
                    		set output_directory $var_val
			} else {
                    		puts "Unknown Tool Variable: $var_name" 
				valid_variables
                    	}
                } else {
                    puts "Usage: setVar <VarName> <Value>"
	     	    valid_variables
                }
            }

	    "getVar" {
                if {[llength $parts] == 2} {
			set var_name [lindex $parts 1]
			if {$var_name eq "lm_gate_dir"} {
                    		puts "lm_gate_dir=$gates_directory"
			} elseif  {$var_name eq  "lm_out_dir"} {
                    		puts "lm_out_dir=$output_directory"
			} else {
                    		puts "Unknown Tool Variable: $var_name" 
				valid_variables
                    	}
                } else {
                    puts "Usage: getVar <VarName>"
		    valid_variables
                }
            }

            "getLibCells" {
                # Call the list-cells function to list gates
                list_gates $gates_directory
            }
            "makeOutput" {
                # Call the list-cells function to list gates
                make_output_folder $gates_directory $output_directory
            }
            "setInput" {
                if {[llength $parts] == 3 && [lindex $parts 1] eq "-cell"} {
                    set gate_name [lindex $parts 2]
                    open_user_input $gate_name $gates_directory
                } else {
                    puts "Usage: setInput -cell CELLNAME"
                }
            }
            "genDataset" {
                # Call the genDataset function to initiate dataset generation
                gen_dataset {*}[lrange $parts 1 end]
            }
            "viewDataset" {
    		if {[llength $parts] == 5 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-file_name"} {
    		    set gate_name [lindex $parts 2]
    		    set file_name [lindex $parts 4]
    		    view_dataset $gate_name $file_name $output_directory
    		} else {
    		    puts "Usage: viewDataset -cell CELLNAME -file_name FILE_NAME"
    		}
	    }
            "loadData" {
    		if {[llength $parts] == 5 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-file_name"} {
        	    set gate_name [lindex $parts 2]
        	    set file_name [lindex $parts 4]
        	    load_data $gate_name $file_name $gates_directory $output_directory
    		} else {
    		    puts "Usage: loadData -cell CELLNAME -file_name FILE_NAME"
    		}
	    }
	    "plotData" {
    		if {[llength $parts] == 5 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-file_name"} {
        	    set gate_name [lindex $parts 2]
        	    set file_name [lindex $parts 4]
        	    plot_data $gate_name $file_name $gates_directory $output_directory
    		} else {
    		    puts "Usage: plotData -cell CELLNAME -file_name FILE_NAME"
    		}
	    }
            "infoData" {
    		if {[llength $parts] == 5 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-file_name"} {
    		    set gate_name [lindex $parts 2]
    		    set file_name [lindex $parts 4]
    		    info_data $gate_name $file_name $gates_directory $output_directory
    		} else {
   		     puts "Usage: infoData -cell CELLNAME -file_name FILE_NAME"
   		}
	    }
	    "splitData" {
    		if {[llength $parts] == 7 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-file_name" && [lindex $parts 5] eq "-test_size"} {
    		    set gate_name [lindex $parts 2]
    		    set file_name [lindex $parts 4]
    		    set test_size [lindex $parts 6]
    		    split_data $gate_name $file_name $test_size $gates_directory $output_directory
    		} else {
    		    puts "Usage: splitData -cell CELLNAME -file_name FILE_NAME -test_size TEST_SIZE"
    		}
	    }
	    "preProcessData_train" {
    		if {[llength $parts] == 3 && [lindex $parts 1] eq "-cell"} {
    		    set gate_name [lindex $parts 2]
    		    preProcessData_train $gate_name $gates_directory $output_directory
    		} else {
    		    puts "Usage: preProcessData_train -cell CELLNAME"
    		}
	    }
	    "preProcessData_test" {
    		if {[llength $parts] == 3 && [lindex $parts 1] eq "-cell"} {
    		    set gate_name [lindex $parts 2]
    		    preProcessData_test $gate_name $gates_directory $output_directory
    		} else {
    		    puts "Usage: preProcessData_test -cell CELLNAME"
    		}
	    }
	    "trainModel" {
                if {[llength $parts] == 5 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-output"} {
                    set gate_name [lindex $parts 2]
                    set model_name [lindex $parts 4]
                    train_model $gate_name $model_name $gates_directory $output_directory
                } else {
                    puts "Usage: trainModel -cell CELLNAME -output MODELNAME"
                }
            }
	    "testModel" {
    		if {[llength $parts] == 7 && [lindex $parts 1] eq "-cell" && [lindex $parts 3] eq "-load" && [lindex $parts 5] eq "-report"} {
    		    set gate_name [lindex $parts 2]
    		    set model_name [lindex $parts 4]
    		    set report_name [lindex $parts 6]
    		    test_model $gate_name $model_name $report_name $gates_directory $output_directory
    		} else {
    		    puts "Usage: testModel -cell CELLNAME -load MODELNAME -report REPORTNAME"
    		}
	    }
            "help" {
                # Display help message with available commands
                display_available_commands
            }
            "exit" {
                # Exit the tool
                puts ""
       	        puts "Exiting LiMo-S shell."
                puts ""
                exit
            }
            default {
                puts "Unknown command. Type 'help' for a list of available commands."
            }
        }
    }
}

# Execute the LiMo-S tool
execute_LiMo-S_tool
