# Import necessary libraries
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import LabelEncoder

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

# Check if a custom data path is provided as a command-line argument
if len(sys.argv) > 1:
    custom_data_path = sys.argv[1]
else:
    custom_data_path = None

# Load data using the provided or default path
data = load_data(custom_data_path)

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

data = encode_process_column(data)

def prepare_and_convert_data(data):
    """
    Prepare and convert specific columns in the data to float.

    Parameters:
    - data (pd.DataFrame): The data as a Pandas DataFrame.

    Returns:
    - pd.DataFrame: The data with converted columns.
    """

    # Select specific columns to keep
    selected_columns = ['process', 'voltage', 'temperature', 'load', 'slew_d', 'slew_clk', 'setup_skew', 'hold_skew', 'ckq_delay']

    data = data[selected_columns]

    # Specify the columns to convert to float
    columns_to_convert = ['process', 'voltage', 'temperature', 'load', 'slew_d', 'slew_clk', 'setup_skew', 'hold_skew', 'ckq_delay']

    # Remove leading and trailing spaces from column names
    data.columns = data.columns.str.strip()

    # Attempt to convert the specified columns to float with error handling
    for column in columns_to_convert:
        try:
            data[column] = data[column].astype(float)
        except ValueError as e:
            print(f"Error converting column '{column}' to float:")
            print(e)
            # If you want to see the problematic rows as well, you can uncomment the following line
            # print(data[data[column].apply(lambda x: not isinstance(x, (int, float)))])
            # You can choose to handle these rows based on your specific use case.

    return data

data = prepare_and_convert_data(data)

def visualize_pairplot(data, save_path, label_fontsize=15, title_fontsize=15, plot_title="Pairplot", dpi=300):
    """
    Visualize the data using a pairplot and save it to a file.

    Parameters:
    - data (pd.DataFrame): The data as a Pandas DataFrame.
    - label_fontsize (int): Font size for x-axis and y-axis labels.
    - title_fontsize (int): Font size for diagonal variable names.
    - plot_title (str): Title for the pairplot.
    - dpi (int): Dots per inch for the figure resolution.
    - save_path (str): Path to save the pairplot visualization.

    Returns:
    - None: Saves the pairplot visualization to the specified file.
    """
    # Set the figure size and DPI for higher resolution
    plt.figure(figsize=(10, 8), dpi=dpi)

    # Create a pairplot to visualize relationships between variables
    pairplot = sns.pairplot(data=data)

    # Customize x-axis and y-axis labels font size
    for ax in pairplot.axes.flat:
        ax.xaxis.label.set_fontsize(label_fontsize)
        ax.yaxis.label.set_fontsize(label_fontsize)
    
    # Increase font size for diagonal variable names
    for i in range(len(data.columns)):
        pairplot.axes[i, i].xaxis.label.set_fontsize(title_fontsize)
        pairplot.axes[i, i].yaxis.label.set_fontsize(title_fontsize)
    
    # Add a title to the pairplot
    pairplot.fig.suptitle(plot_title, fontsize=20)
    
    # Save the pairplot to the specified file
    pairplot.savefig(save_path)

if __name__ == "__main__":
    if len(sys.argv) > 3:
        file_path = sys.argv[1]
        output_directory = sys.argv[2]
        gate_name = sys.argv[3]
    else:
        file_path = ""
        output_directory = ""
        gate_name = ""

    save_path = os.path.join(output_directory, gate_name, "dataset_visualization.png")
    absolute_path = os.path.abspath(save_path)

    visualize_pairplot(data, absolute_path)
    print("Plot saved in absolute_path:", absolute_path)
