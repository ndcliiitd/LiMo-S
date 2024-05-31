# For data manipulation and analysis
import pandas as pd  
# For numerical operations and array handling
import numpy as np  
# For splitting the data
from sklearn.model_selection import train_test_split 
# For label encoding categorical data
from sklearn.preprocessing import LabelEncoder  
# For building a neural network regressor
from sklearn.neural_network import MLPRegressor 
# For shuffling the data
from sklearn.utils import shuffle  
# For evaluating model performance
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score 
from sklearn.model_selection import KFold
# For creating plots and visualizations
import matplotlib.pyplot as plt
# For measuring time
import time 
import argparse
import joblib
import os
import sys

def load_data_X_train(data_path):
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

def load_data_y_train(data_path):
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



# Function to train and evaluate an MLP Regressor and save the trained model
def train_and_evaluate_mlp_regressor_cv_save_model(X, y, model_name, output_directory, gate_name, max_iter=300, verbose=True, n_splits=5, batch_size=5000):
    """
    Train an MLP Regressor with k-fold cross-validation, evaluate the model on each fold, and save the trained model.

    Parameters:
    - X (pd.DataFrame): The feature data.
    - y (pd.DataFrame): The true target values.
    - model_name (str): The name of the model to save (without the .pkl extension).
    - max_iter (int): Maximum number of iterations for training.
    - verbose (bool): Whether to display training progress.
    - n_splits (int): Number of splits for cross-validation.
    - batch_size (int or None): Batch size for training. If None, no batching is used.

    Returns:
    - list of dictionaries, each containing evaluation metrics for a fold.
    """

    kf = KFold(n_splits=n_splits, shuffle=True)
    evaluation_results = []  # List to store evaluation results for each fold

    for train_index, valid_index in kf.split(X):
        X_train_fold, X_valid_fold = X.iloc[train_index], X.iloc[valid_index]
        y_train_fold, y_valid_fold = y.iloc[train_index], y.iloc[valid_index]

        regressor = MLPRegressor(hidden_layer_sizes=(100, 50, 50),
                                 max_iter=max_iter, learning_rate='adaptive', learning_rate_init=0.001,
                                 activation='relu', alpha=0.01, solver='adam', verbose=verbose,
                                 batch_size=batch_size)

        regressor.fit(X_train_fold, y_train_fold)

        # Evaluate the model on the validation fold
        y_pred_valid = regressor.predict(X_valid_fold)
        mse = mean_squared_error(y_valid_fold, y_pred_valid)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_valid_fold, y_pred_valid)
        r2 = r2_score(y_valid_fold, y_pred_valid)

        evaluation_result = {
            "MSE": mse,
            "RMSE": rmse,
            "MAE": mae,
            "R2 Score": r2
        }

        evaluation_results.append(evaluation_result)

    # Select the model with the lowest RMSE from the list of trained models
    best_model_index = np.argmin([result['RMSE'] for result in evaluation_results])
    regressor = regressor  # Updated model variable name

    # Save the trained model with the specified name in the results folder
    model_path = os.path.join(output_directory, gate_name, f"{model_name}.pkl")
    joblib.dump(regressor, model_path)

    return evaluation_results

if __name__ == "__main__":
    if len(sys.argv) > 3:        
        gate_name = sys.argv[1]
        model_name = sys.argv[2]
        output_directory = sys.argv[3]
    else:
        gate_name = ""
        model_name = ""
        output_directory = ""

    gates_path_X_train = os.path.join(output_directory, gate_name, "preprocessed_X_train.csv")
    X_train = load_data_X_train(gates_path_X_train)

    gates_path_y_train = os.path.join(output_directory, gate_name, "preprocessed_y_train.csv")
    y_train = load_data_y_train(gates_path_y_train)


    if gate_name is not None and model_name is not None:
  
        # Perform k-fold cross-validation and save the model
        evaluation_results = train_and_evaluate_mlp_regressor_cv_save_model(X_train, y_train, model_name, output_directory, gate_name, batch_size=32)

        # Aggregate and print the evaluation results
        print("Evaluation Results:")
        for i, result in enumerate(evaluation_results):
            print(f"Fold {i + 1}:")
            for metric, value in result.items():
                print(f"{metric}: {value:.4f}")
            print()
    
    else:
        print("Usage: trainModel -gate (gate name) -output (model name)")

#trainModel -cell DFFQX1 -output trained_model_DFFQX1
