import sys
import pandas as pd

def load_data(data_path):
    """
    Load and preprocess the data from the specified path.

    Parameters:
    - data_path (str): The path to the data file.

    Returns:
    - pd.DataFrame: The data as a Pandas DataFrame.
    """

    # Define column headers
    data_head = ['load', 'slew_d', 'slew_clk', 'process', 'voltage', 'temperature', 'skew_clk', 'setup_skew', 'hold_skew', 'ckq_delay']

    if data_path:
        # Load the data from the CSV file at the provided data_path
        data = pd.read_csv(data_path, header=None, names=data_head, encoding='latin-1')
    
    # Drop the first two rows and reset the index
    data = data.drop([0]).reset_index(drop=True)

    # Drop rows with missing values
    data = data.dropna()

    return data

# Check if a custom data path is provided as a command-line argument
if len(sys.argv) > 1:
    custom_data_path = sys.argv[1]
else:
    custom_data_path = None

# Load data using the provided or default path
data = load_data(custom_data_path)

print(data)
#loadData -gate nand2x1 -file_name GPr3_main_dataset_NAND2X1.csv
