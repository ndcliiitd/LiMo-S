# For data manipulation and analysis
import pandas as pd
import argparse
from sklearn.model_selection import train_test_split
import os
import sys

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

def prepare_data(data):
    """
    Prepare the input features (X) and target labels (y) from the data.

    Parameters:
    - data (pd.DataFrame): The data as a Pandas DataFrame.

    Returns:
    - pd.DataFrame: The input features (X).
    - pd.DataFrame: The target labels (y).
    """
    X = data[['process', 'voltage', 'temperature', 'load', 'slew_d', 'slew_clk', 'setup_skew', 'hold_skew']]
    y = data[['ckq_delay']]
    return X, y

def split_data(X, y, test_size):
    """
    Split the data into training and testing sets.

    Parameters:
    - X (pd.DataFrame): The input features.
    - y (pd.DataFrame): The target labels.
    - test_size (float): The proportion of the data to include in the testing set.

    Returns:
    - pd.DataFrame: The training features (X_train).
    - pd.DataFrame: The testing features (X_test).
    - pd.DataFrame: The training target labels (y_train).
    - pd.DataFrame: The testing target labels (y_test).
    """

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

    return X_train, X_test, y_train, y_test

# Load the data

if __name__ == "__main__":
    if len(sys.argv) > 4:
        file_path = sys.argv[1]
        test_size = sys.argv[2]
        output_directory = sys.argv[3]
        gate_name = sys.argv[4]
    else:
        file_path = ""
        test_size = ""
        output_directory = ""
        gate_name = ""

    data = load_data(file_path)
    X, y = prepare_data(data)

    # Split the data
    test_size = float(test_size)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size)

    output_directory = os.path.join(output_directory, gate_name)

    # Define file paths for saving the data
    X_train_file = os.path.join(output_directory, 'X_train.csv')
    y_train_file = os.path.join(output_directory, 'y_train.csv')
    X_test_file = os.path.join(output_directory, 'X_test.csv')
    y_test_file = os.path.join(output_directory, 'y_test.csv')
 
    print("X_train, Y_train, X_test, y_test is generated in folder:", output_directory)

    # Save the data to CSV files
    X_train.to_csv(X_train_file, index=False)
    y_train.to_csv(y_train_file, index=False)
    X_test.to_csv(X_test_file, index=False)
    y_test.to_csv(y_test_file, index=False)
    
##splitData -cell DFFQX1 -file_name GPr3_main_dataset_DFFQX1.csv -test_size 0.2

