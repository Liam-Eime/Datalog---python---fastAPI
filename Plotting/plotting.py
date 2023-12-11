"""
Plotting script for plotting the .csv data from the HTTP request from the Python web application.

Author: Liam Eime
Date: 11/12/2023
"""

def main():
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
        plt.figure("High Frequency Accelerations")
        plt.xlabel('Time')
        plt.ylabel("Acceleration (g's)")
        plt.title("High Frequency Acceleration Data")
        try:  # plot high frequency acceleration data
            high_freq_df = files.read_latest_csv_to_dataframe(PATH_TO_HF_DATA_FOLDER)
            high_freq_timestamps = pd.to_datetime(high_freq_df["Timestamp"].astype(str), format='mixed')
            accelerometer1_x = high_freq_df["Accelerometer1.X"].astype(float)
            accelerometer1_y = high_freq_df["Accelerometer1.Y"].astype(float)
            accelerometer1_z = high_freq_df["Accelerometer1.Z"].astype(float)
            accelerometer2_x = high_freq_df["Accelerometer2.X"].astype(float)
            accelerometer2_y = high_freq_df["Accelerometer2.Y"].astype(float)
            accelerometer2_z = high_freq_df["Accelerometer2.Z"].astype(float)
            plt.plot(high_freq_timestamps, accelerometer1_x, label='Accelerometer1.X', color='red')
            plt.plot(high_freq_timestamps, accelerometer1_y, label='Accelerometer1.Y', color='blue')
            plt.plot(high_freq_timestamps, accelerometer1_z, label='Accelerometer1.Z', color='green')
            plt.plot(high_freq_timestamps, accelerometer2_x, label='Accelerometer2.X', color='black')
            plt.plot(high_freq_timestamps, accelerometer2_y, label='Accelerometer2.Y', color='orange')
            plt.plot(high_freq_timestamps, accelerometer2_z, label='Accelerometer2.Z', color='grey')
            plt.legend()
            plt.draw()
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        except Exception:
            pass

        plt.figure("Low Frequency Temperature")
        plt.xlabel('Time')
        plt.ylabel('Temperature (deg C)')
        plt.title("Low Frequency Temperature Data")
        try:  # plot low frequency temperature data
            low_freq_df = files.read_latest_csv_to_dataframe(PATH_TO_LF_DATA_FOLDER)
            low_freq_timestamps = pd.to_datetime(low_freq_df["Timestamp"].astype(str), format="%Y-%m-%d %H:%M:%S")
            temperature = low_freq_df["Temperature"].astype(float)
            plt.plot(low_freq_timestamps, temperature, label='Temperature', color='red', marker='*')
            plt.draw()
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        except Exception:
            pass

        plt.pause(PAUSE_TIME_S)
        plt.figure("High Frequency Accelerations").clear()
        plt.figure("Low Frequency Temperature").clear()

if __name__ == '__main__':
    # import libraries
    from matplotlib import pyplot as plt
    from matplotlib import dates as mdates
    from dotenv import load_dotenv
    import pandas as pd
    import os
    import sys
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)
    import files
    main()