# main.py

from fastapi import FastAPI, Request
import os
import csv
import numpy as np

OUTPUT_DIR = r'W:\2023\Datalog - python - fastAPI\Logger Data'
MAX_LOW_FREQ_DATA_ROWS = 120  # This value is 2 * how many minutes of temp data acquired
TEMPORARY_LOW_FREQ_DATA_PATH = os.path.join(OUTPUT_DIR, r'lowfreqdata%s.csv' % 0)
LOW_FREQ_HEADER = ["Timestamp",
                   "Accelerometer1.Max.X", "Accelerometer1.Max.Y", "Accelerometer1.Max.Z",
                   "Accelerometer2.Max.X", "Accelerometer2.Max.Y", "Accelerometer2.Max.Z",
                   "Accelerometer1.Min.X", "Accelerometer1.Min.Y", "Accelerometer1.Min.Z",
                   "Accelerometer2.Min.X", "Accelerometer2.Min.Y", "Accelerometer2.Min.Z",
                   "Temperature"]
low_freq_data_path = ''

TEMPORARY_HIGH_FREQ_DATA_PATH = os.path.join(OUTPUT_DIR, r'highfreqdata%s.csv' % 0)
HIGH_FREQ_HEADER = ["Timestamp",
                    "Accelerometer1.X", "Accelerometer1.Y", "Accelerometer1.Z",
                    "Accelerometer2.X", "Accelerometer2.Y", "Accelerometer2.Z"]

app = FastAPI()
    
@app.post("/uploadLowFreq/{logger_filename}")
async def upload_low_freq(
    logger_filename: str, 
    request: Request
):
    raw_bytes = await request.body()
    raw_data = raw_bytes.decode("utf-8").strip("\r\n")
    low_freq_data = raw_data.replace('"', '')
    low_freq_data = low_freq_data.split(",")
    low_freq_data = dict(zip(LOW_FREQ_HEADER, low_freq_data))
    continue_with_file = True
    global low_freq_data_path
    try:
        with open(low_freq_data_path, 'r') as f:
            low_freq_data_rows_count = len(f.readlines())
        if low_freq_data_rows_count >= MAX_LOW_FREQ_DATA_ROWS + 1:  # +1 due to header
            continue_with_file = False
    except Exception:
        if low_freq_data_path != '':
            print('an error occured when trying to read existing file')
        pass
    try:
        if continue_with_file:
            os.rename(low_freq_data_path, TEMPORARY_LOW_FREQ_DATA_PATH)
    except Exception:
        pass
    try:
        file_exists = os.path.exists(TEMPORARY_LOW_FREQ_DATA_PATH)
        with open(TEMPORARY_LOW_FREQ_DATA_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=LOW_FREQ_HEADER)
            if not file_exists:
                writer.writeheader()
            writer.writerow(low_freq_data)
        with open(TEMPORARY_LOW_FREQ_DATA_PATH, 'r') as f:
            f.readline()  # Read header to skip header
            first_entry = f.readline().strip("\r\n").split(",")
        initial_timestamp = first_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        with open(TEMPORARY_LOW_FREQ_DATA_PATH, 'rb') as f:
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_entry = f.readline().decode().strip("\r\n").split(",")
        latest_timestamp = last_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        total_timestamp = f"{initial_timestamp}-{latest_timestamp}"
        low_freq_data_path = os.path.join(OUTPUT_DIR, r'lowfreqdata %s.csv' % total_timestamp)
        os.rename(TEMPORARY_LOW_FREQ_DATA_PATH, low_freq_data_path)
    except Exception:
        return {"message": "There was an error uploading the file"}
    return {"message": "successfully uploaded low frequency data"}

@app.post("/uploadHighFreqAccel/{logger_filename}")
async def upload_accelerations(
    logger_filename: str,
    request: Request
):
    raw_bytes = await request.body()
    decoded_data = raw_bytes.decode("utf-8").replace('"', '').replace('\r\n', 'x,').split(",")
    indicies = [(i+1) for i, x in enumerate(decoded_data) if x.endswith('x')]
    decoded_data = [each_split.tolist() for each_split in np.split(decoded_data, indicies) if len(each_split)]
    high_freq_data_lists = [[item.replace('x', '') for item in lst] for lst in decoded_data]
    high_freq_data = [dict(zip(HIGH_FREQ_HEADER, hf_list)) for hf_list in high_freq_data_lists]
    
    try:
        with open(TEMPORARY_HIGH_FREQ_DATA_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=HIGH_FREQ_HEADER)
            writer.writeheader()
            writer.writerows(high_freq_data)
        with open(TEMPORARY_HIGH_FREQ_DATA_PATH, 'r') as f:
            f.readline()  # Read header to skip header
            first_entry = f.readline().strip("\r\n").split(",")
        initial_timestamp = first_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        with open(TEMPORARY_HIGH_FREQ_DATA_PATH, 'rb') as f:
            num_newlines = 0
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while num_newlines < 2:
                    f.seek(-2, os.SEEK_CUR)
                    if f.read(1) == b'\n':
                        num_newlines += 1
            except OSError:
                f.seek(0)
            last_entry = f.readline().decode().strip("\r\n").split(",")
        latest_timestamp = last_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        total_timestamp = f"{initial_timestamp}-{latest_timestamp}"
        high_freq_data_path = os.path.join(OUTPUT_DIR, r'highfreqdata %s.csv' % total_timestamp)
        os.rename(TEMPORARY_HIGH_FREQ_DATA_PATH, high_freq_data_path)
    except Exception:
        return {"message": "There was an error uploading the file"}

    return {"message": "successfully uploaded high frequency data"}