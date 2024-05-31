# For data visualization using seaborn
import seaborn as sns
# For creating plots and visualizations
import matplotlib.pyplot as plt
# For data manipulation and analysis
import pandas as pd  
# For numerical operations and array handling
import numpy as np  
# For label encoding categorical data
from sklearn.preprocessing import LabelEncoder 
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

def encode_process_column(data):
    """
    Encode the 'process' column in the data using Label Encoding.

    Parameters:
    - data (pd.DataFrame): The data as a Pandas DataFrame.

    Returns:
    - pd.DataFrame: The data with the 'process' column encoded.
    - LabelEncoder: The LabelEncoder used for encoding.
    """
    le = LabelEncoder()
    data['process'] = le.fit_transform(data['process'])
    return data


def prepare_and_convert_data(data):
    """
    Prepare and convert all columns in the data to float.

    Parameters:
    - data (pd.DataFrame): The data as a Pandas DataFrame.

    Returns:
    - pd.DataFrame: The data with all columns converted to float.
    """
    # Convert all columns to float
    data = data.astype(float)

    return data



class MinMaxScaler:
    """
    Min-Max Scaler class for scaling and inverse scaling of data.

    Attributes:
    - min_vals (numpy.ndarray): The minimum values of the scaled data.
    - max_vals (numpy.ndarray): The maximum values of the scaled data.
    """

    def __init__(self):
        self.min_vals = None
        self.max_vals = None

    def fit(self, X_min_max):
        """
        Fit the scaler on the provided data to compute min and max values.

        Parameters:
        - X_min_max (numpy.ndarray): The data used for fitting the scaler.

        Returns:
        - None
        """
        self.min_vals = np.min(X_min_max, axis=0)
        self.max_vals = np.max(X_min_max, axis=0)
        
    def transform(self, X):
        """
        Scale the input data using the computed min and max values.

        Parameters:
        - X (numpy.ndarray): The input data to be scaled.

        Returns:
        - numpy.ndarray: The scaled data.
        """
        return (X - self.min_vals) / (self.max_vals - self.min_vals)

    def fit_transform(self, X_min_max, X):
        """
        Fit the scaler on the provided data and scale the input data.

        Parameters:
        - X_min_max (numpy.ndarray): The data used for fitting the scaler.
        - X (numpy.ndarray): The input data to be scaled.

        Returns:
        - numpy.ndarray: The scaled data.
        """
        self.fit(X_min_max)
        return self.transform(X)

    def inverse_transform(self, X_scaled):
        """
        Inverse scale the input data to the original range.

        Parameters:
        - X_scaled (numpy.ndarray): The scaled data to be inverse transformed.

        Returns:
        - numpy.ndarray: The inverse transformed data.
        """
        return (X_scaled * (self.max_vals - self.min_vals)) + self.min_vals

    
# Create MinMaxScaler instances for feature scaling
scaler = MinMaxScaler()


def clean_data(data):
    """
    Clean the data by replacing infinite values with NaN and filling NaN values with zeros.

    Parameters:
    - data (pd.DataFrame): The data as a Pandas DataFrame.

    Returns:
    - pd.DataFrame: The cleaned data.
    """
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.fillna(0, inplace=True)
    #data = shuffle(data)
    return data


def preprocess_data(train_data, test_data):
    """
    Preprocess the training and testing datas.

    Parameters:
    - train_data (pd.DataFrame): The training data as a Pandas DataFrame.
    - test_data (pd.DataFrame): The testing data as a Pandas DataFrame.

    Returns:
    - pd.DataFrame: The preprocessed training features (X).
    - pd.DataFrame: The preprocessed training target labels (y).
    - pd.DataFrame: The preprocessed testing features (X_test).
    - pd.DataFrame: The preprocessed testing target labels (y_test).
    """
    test_data = clean_data(test_data)

    # Step 4: Apply Min-Max Scaling on X and y
    preprocessed_data = scaler.fit_transform(train_data, test_data)
    preprocessed_data = clean_data(preprocessed_data)
    return preprocessed_data


if __name__ == "__main__":
    if len(sys.argv) > 2:        
        gate_name = sys.argv[1]
        output_directory = sys.argv[2]
    else:
        gate_name = ""
        output_directory = ""

    gates_path_X_train = os.path.join(output_directory, gate_name, "X_train.csv")
    X_train = load_data_X(gates_path_X_train)

    gates_path_y_train = os.path.join(output_directory, gate_name, "y_train.csv")
    y_train = load_data_y(gates_path_y_train)

    X_train = encode_process_column(X_train)
    X_train = prepare_and_convert_data(X_train)
    y_train = prepare_and_convert_data(y_train)

    gates_path_X_test = os.path.join(output_directory, gate_name, "X_test.csv")
    X_test = load_data_X(gates_path_X_test)

    gates_path_y_test = os.path.join(output_directory, gate_name, "y_test.csv")
    y_test = load_data_y(gates_path_y_test)

    X_test = encode_process_column(X_test)
    X_test = prepare_and_convert_data(X_test)
    y_test = prepare_and_convert_data(y_test)

    #Preprocess the data
    preprocessed_X_test = preprocess_data(X_train, X_test)
    preprocessed_y_test = preprocess_data(y_train, y_test)

    data_path_preprocessed_X_test = os.path.join(output_directory, gate_name, "preprocessed_X_test.csv")
    preprocessed_X_test.to_csv(data_path_preprocessed_X_test, index = False)

    data_path_preprocessed_y_test = os.path.join(output_directory, gate_name, "preprocessed_y_test.csv")
    preprocessed_y_test.to_csv(data_path_preprocessed_y_test, index = False)

#preProcessData_test -cell DFFQX1
