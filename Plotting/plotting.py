from matplotlib import pyplot as plt
from dotenv import load_dotenv
import matplotlib as mpl
import numpy as np
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
    print(df["Accelerometer1.X"])
    plt.plot(df["Timestamp"].astype(str), df["Accelerometer1.X"].astype(float))
    plt.show()

if __name__ == '__main__':
    main()