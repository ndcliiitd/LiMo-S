import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import argparse
import os
import sys


def load_data_X(data_path):
    """
    Load and preprocess the data from the specified path.

    Parameters:
    - data_path (str): The path to the data file.

    Returns:
    - pd.DataFrame: The data as a Pandas DataFrame.
    """
    # Define column headers
    data_head = ['process', 'voltage', 'temperature', 'load', 'slew_d', 'slew_clk', 'setup_skew', 'hold_skew']


    if data_path:
        # Load the data from the CSV file at the provided data_path
        data = pd.read_csv(data_path, header=None, names=data_head, encoding='latin-1')

    # Drop the first two rows and reset the index
    data = data.drop([0]).reset_index(drop=True)
    
    # Drop rows with missing values
    data = data.dropna()
    return data

def load_data_y(data_path):
    """
    Load and preprocess the data from the specified path.

    Parameters:
    - data_path (str): The path to the data file.

    Returns:
    - pd.DataFrame: The data as a Pandas DataFrame.
    """

    # Define column headers
    data_head = ['ckq_delay']

    # Load the data from the CSV file
    data = pd.read_csv(data_path, header=None, names=data_head, encoding='latin-1')

    # Drop the first two rows and reset the index
    data = data.drop([0]).reset_index(drop=True)

    # Drop rows with missing values
    data = data.dropna()

    return data

def evaluate_model_and_save_report(X, y, regressor, report_filename):
    """
    Evaluate the model using various metrics and save the results in a report file.

    Parameters:
    - X (pd.DataFrame): Feature data.
    - y (pd.DataFrame): True target values.
    - regressor: Trained regression model.
    - report_filename (str): Name of the report file to save the metrics.

    Returns:
    - dict: A dictionary containing the computed metrics.
    """
    # Making predictions
    y_pred = regressor.predict(X)

    MSE = mean_squared_error(y, y_pred)
    RMSE = np.sqrt(MSE)
    MAE = mean_absolute_error(y, y_pred)
    R2 = r2_score(y, y_pred)

    # Create a dictionary to store the metrics
    metrics_dict = {
        "MSE": MSE,
        "RMSE": RMSE,
        "MAE": MAE,
        "R2 Score": R2
    }

    # Write the metrics to a report file
    with open(report_filename, 'w') as report_file:
        report_file.write("Metrics:\n")
        for metric, value in metrics_dict.items():
            report_file.write(f"{metric}: {value:.4f}\n")

    return metrics_dict

if __name__ == "__main__":
    if len(sys.argv) > 4:        
        gate_name = sys.argv[1]
        model_name = sys.argv[2]
        report_name = sys.argv[3]
        output_directory = sys.argv[4]
    else:
        gate_name = ""
        model_name = ""
        report_name = ""
        output_directory = ""

    if gate_name is not None and model_name is not None and report_name is not None:
        # Load the trained model

        model_path = os.path.join(output_directory, gate_name)
        model_filename = os.path.join(model_path,  model_name)
        regressor = joblib.load(model_filename)
    
        gates_path_X_test = os.path.join(output_directory, gate_name, "preprocessed_X_test.csv")
        X_test = load_data_X(gates_path_X_test)

        gates_path_y_test = os.path.join(output_directory, gate_name, "preprocessed_y_test.csv")
        y_test = load_data_y(gates_path_y_test)
 
        report_filename = os.path.join(output_directory, gate_name, report_name)

        # Evaluate the model on the test data and save the report
        print(f"Evaluate Model on Test data for gate {gate_name}")
        metrics = evaluate_model_and_save_report(X_test, y_test, regressor, report_filename)
        print(metrics)
        print("Metrics saved in", report_filename)
    else:
        print("Usage: testModel -gate (gate name) -load (model name) -report (report name)")

#testModel -cell DFFQX1 -load trained_model_DFFQX1.pkl -report report_DFFQX1.txt
