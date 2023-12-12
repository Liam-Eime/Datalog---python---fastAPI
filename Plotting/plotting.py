"""
Plotting script for plotting the .csv data from the HTTP request from the Python web application.

Author: Liam Eime
Date: 12/12/2023
"""

# import libraries
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from dotenv import load_dotenv
from typing import Optional
import pandas as pd
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import files

def plot_data(
    title: str, 
    x_label: str, 
    y_label: str, 
    timestamps: list[str], 
    data: list[list[float]], 
    labels: list[str], 
    colors: list[str],
    marker: Optional[str] = None
):
    """
    #### Plot data

    ##### Parameters:
    - title: str
        - title of the plot
    - x_label: str
        - x axis label
    - y_label: str
        - y axis label
    - timestamps: list[str]
        - list of timestamps
    - data: list[list[float]]
        - list of lists of data to plot
    - labels: list[str]
        - list of labels for each data set
    - colors: list[str]
        - list of colors for each data set
    - marker: Optional[str] = None
        - marker to use for the plot

    ##### Returns:
    - None
    """
    plt.figure(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    for i in range(len(data)):
        plt.plot(timestamps, data[i], label=labels[i], color=colors[i], marker=marker)
    plt.legend()
    plt.draw()
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

def plot_high_freq_data(path_to_hf_data_folder: str):
    """
    #### Plot high frequency data

    ##### Parameters:
    - path_to_hf_data_folder: str
        - path to high frequency data folder

    ##### Returns:
    - None
    """
    high_freq_df = files.read_latest_csv_to_dataframe(path_to_hf_data_folder)
    high_freq_timestamps = pd.to_datetime(high_freq_df["Timestamp"].astype(str), format='mixed')
    data = [high_freq_df[column].astype(float) for column in high_freq_df.columns if column != "Timestamp"]
    labels = [column for column in high_freq_df.columns if column != "Timestamp"]
    colors = ['red', 'blue', 'green', 'black', 'orange', 'grey']
    plot_data("High Frequency Accelerations", 'Time', "Acceleration (g's)", high_freq_timestamps, data, labels, colors)

def plot_low_freq_data(path_to_lf_data_folder: str):
    """
    #### Plot low frequency data

    ##### Parameters:
    - path_to_lf_data_folder: str
        - path to low frequency data folder

    ##### Returns:
    - None
    """
    low_freq_df = files.read_latest_csv_to_dataframe(path_to_lf_data_folder)
    low_freq_timestamps = pd.to_datetime(low_freq_df["Timestamp"].astype(str), format="%Y-%m-%d %H:%M:%S")
    data = [low_freq_df["Temperature"].astype(float)]
    labels = ["Temperature"]
    colors = ['red']
    plot_data("Low Frequency Temperature", 'Time', "Temperature (deg C)", low_freq_timestamps, data, labels, colors, marker='*')

def main():
    """
    #### Main function for plotting script
    """
    # load environment variables
    load_dotenv()
    OUTPUT_DIR = os.getenv('OUTPUT_DIR')
    OUTPUT_FOLDER_HIGH_FREQ = os.getenv('OUTPUT_FOLDER_HIGH_FREQ')
    OUTPUT_FOLDER_LOW_FREQ = os.getenv('OUTPUT_FOLDER_LOW_FREQ')
    # set variables
    PATH_TO_HF_DATA_FOLDER = os.path.join(OUTPUT_DIR, OUTPUT_FOLDER_HIGH_FREQ)
    PATH_TO_LF_DATA_FOLDER = os.path.join(OUTPUT_DIR, OUTPUT_FOLDER_LOW_FREQ)
    PAUSE_TIME_S = 5

    plt.ion()
    plt.show()
    while True:
        try:
            plot_high_freq_data(PATH_TO_HF_DATA_FOLDER)
            plot_low_freq_data(PATH_TO_LF_DATA_FOLDER)
        except Exception:
            pass
        finally:
            plt.pause(PAUSE_TIME_S)
            plt.figure("High Frequency Accelerations").clear()
            plt.figure("Low Frequency Temperature").clear()

if __name__ == '__main__':
    main()