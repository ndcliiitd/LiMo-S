# For data manipulation and analysis
import pandas as pd
import sys
import os

def load_data(data_path):
    """
    Load and preprocess the data from the specified path.

    Parameters:
    - data_path (str): The path to the data file.

    Returns:
    - pd.DataFrame: The data as a Pandas DataFrame.
    """
    # Define column headers
    data_head = ['load', 'slew_d', 'slew_clk', 'process', 'voltage', 'temperature', 'skew_d', 'setup_skew', 'hold_skew', 'ckq_delay', 'D', 'Q', 'D_Q_comparision']


    if data_path:
        # Load the data from the CSV file at the provided data_path
        data = pd.read_csv(data_path, header=None, names=data_head, encoding='latin-1')

    # Drop the first two rows and reset the index
    data = data.drop([0]).reset_index(drop=True)

    # Drop rows with missing values
    data = data.dropna()
    data = data[[ 'process', 'voltage', 'temperature', 'load', 'slew_d', 'slew_clk', 'setup_skew', 'hold_skew', 'ckq_delay']]

    return data



def info_data(data):
    # Display the last 5 rows of the data
    print("\033[1mLast 5 rows of the data\n\033[0m")
    rows = data.tail()
    print(rows)

    # Display information about the data (number of rows, columns, data types)
    print("\n\033[1mInformation about data (number of rows, columns, data types)\n\033[0m")
    info = data.info()

    # Display basic statistics about the data
    print("\n\033[1mInformation about data statistics\n\033[0m")
    stats = data.describe().transpose()
    print(stats)

    # Return the last 5 rows, prints data information, and statistics to the console
    return rows, info, stats


def info_data_and_save(data, absolute_path):
    # Create a file to save the information
    with open(absolute_path, 'w') as info_file:
        # Display the last 5 rows of the data
        info_file.write("\033[1mLast 5 rows of the data\n\033[0m")
        rows = data.tail()
        info_file.write(rows.to_string() + "\n\n")

        # Display information about the data (number of rows, columns, data types)
        info_file.write("\n\033[1mInformation about data (number of rows, columns, data types)\n\033[0m")
        info = data.info(buf=info_file)

        # Display basic statistics about the data
        info_file.write("\n\033[1mInformation about data statistics\n\033[0m")
        stats = data.describe().transpose()
        info_file.write(stats.to_string() + "\n")

    return rows

# Extract the data path from the command arguments
if len(sys.argv) > 1:
    data_path = sys.argv[1]

# Load the data
data = load_data(data_path)
if __name__ == "__main__":
    if len(sys.argv) > 3:
        file_path = sys.argv[1]
        output_directory = sys.argv[2]
        gate_name = sys.argv[3]
    else:
        file_path = ""
        output_directory = ""
        gate_name = ""

    save_path = os.path.join(output_directory, gate_name, "info.txt")
    absolute_path = os.path.abspath(save_path)

    # Call the function and display information about the data
    data_info = info_data(data)

    # Call the function and save information about the data to the info.txt file
    print("\nDisplaying data information and saving to\n", save_path)
    last_5_rows = info_data_and_save(data, save_path)

#infoData -cell DFFQX1 -file_name GPr3_main_dataset_DFFQX1.csv

