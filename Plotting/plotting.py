from matplotlib import pyplot as plt
from dotenv import load_dotenv
import pandas as pd
import os

def main():
    load_dotenv()
    OUTPUT_FOLDER_HIGH_FREQ = os.getenv('OUTPUT_FOLDER_HIGH_FREQ')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR')
    DIR = os.path.join(OUTPUT_DIR, OUTPUT_FOLDER_HIGH_FREQ)

    list_of_files = [os.path.abspath(name) for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]
    newest = sorted([os.path.join(DIR, f) for f in os.listdir(DIR)], key=os.path.getctime)[len(list_of_files) - 1]
    df = pd.read_csv(newest)

    timestamps = pd.to_datetime(df["Timestamp"].astype(str), format='mixed')
    accelerometer1_x = df["Accelerometer1.X"].astype(float)
    accelerometer1_y = df["Accelerometer1.Y"].astype(float)
    accelerometer1_z = df["Accelerometer1.Z"].astype(float)
    accelerometer2_x = df["Accelerometer2.X"].astype(float)
    accelerometer2_y = df["Accelerometer2.Y"].astype(float)
    accelerometer2_z = df["Accelerometer2.Z"].astype(float)

    plt.plot(timestamps, accelerometer1_x, label='Accelerometer1.X')
    plt.plot(timestamps, accelerometer1_y, label='Accelerometer1.Y')
    plt.plot(timestamps, accelerometer1_z, label='Accelerometer1.Z')
    plt.plot(timestamps, accelerometer2_x, label='Accelerometer2.X')
    plt.plot(timestamps, accelerometer2_y, label='Accelerometer2.Y')
    plt.plot(timestamps, accelerometer2_z, label='Accelerometer2.Z')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel("Acceleration (g's)")
    plt.show()

if __name__ == '__main__':
    main()