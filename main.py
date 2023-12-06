# main.py

from fastapi import FastAPI, Request, Depends
from functools import lru_cache
from datetime import datetime
import config
import os
import csv
import json
import numpy as np

low_freq_data_path = ''
prev_high_freq_data_path = ''

app = FastAPI()

@lru_cache
def get_settings():
    return config.Settings()
    
@app.post("/uploadLowFreq/{logger_filename}")
async def upload_low_freq(
    logger_filename: str, 
    request: Request,
    settings: config.Settings = Depends(get_settings)
):
    OUTPUT_DIR = settings.output_dir
    TEMP_LOW_FREQ_DATA_PATH = os.path.join(OUTPUT_DIR, settings.temp_low_freq_filename)
    raw_bytes = await request.body()
    raw_data = raw_bytes.decode("utf-8").strip("\r\n")
    low_freq_data = raw_data.replace('"', '')
    low_freq_data = low_freq_data.split(",")
    low_freq_header = json.loads(settings.low_freq_header)
    low_freq_data = dict(zip(low_freq_header, low_freq_data))
    continue_with_file = True
    global low_freq_data_path
    try:
        with open(low_freq_data_path, 'r') as f:
            low_freq_data_rows_count = len(f.readlines())
        if low_freq_data_rows_count >= settings.max_low_freq_data_rows + 1:  # +1 due to header
            continue_with_file = False
    except Exception:
        if low_freq_data_path != '':
            print('an error occured when trying to read existing file')
        pass
    try:
        if continue_with_file:
            os.rename(low_freq_data_path, TEMP_LOW_FREQ_DATA_PATH)
    except Exception:
        pass  # do nothing because only error when attempting to rename non-existent file on first event
    try:
        file_exists = os.path.exists(TEMP_LOW_FREQ_DATA_PATH)
        with open(TEMP_LOW_FREQ_DATA_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=low_freq_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(low_freq_data)
        with open(TEMP_LOW_FREQ_DATA_PATH, 'r') as f:
            f.readline()  # read header to skip header
            first_entry = f.readline().strip("\r\n").split(",")
        initial_timestamp = first_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        with open(TEMP_LOW_FREQ_DATA_PATH, 'rb') as f:
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_entry = f.readline().decode().strip("\r\n").split(",")
        latest_timestamp = last_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        total_timestamp = f"{initial_timestamp}-{latest_timestamp}"
        output_filename = settings.output_low_freq_filename + ' %s.csv' % total_timestamp
        low_freq_data_path = os.path.join(OUTPUT_DIR, output_filename)
        os.rename(TEMP_LOW_FREQ_DATA_PATH, low_freq_data_path)
    except Exception:
        return {"message": "There was an error uploading the file"}
    return {"message": "successfully uploaded low frequency data"}

@app.post("/uploadHighFreqAccel/{logger_filename}")
async def upload_accelerations(
    logger_filename: str,
    request: Request,
    settings: config.Settings = Depends(get_settings)
):
    OUTPUT_DIR = settings.output_dir
    TEMP_HIGH_FREQ_DATA_PATH = os.path.join(OUTPUT_DIR, settings.temp_high_freq_filename)
    raw_bytes = await request.body()
    decoded_data = raw_bytes.decode("utf-8").replace('"', '').replace('\r\n', 'x,').split(",")
    indicies = [(i+1) for i, x in enumerate(decoded_data) if x.endswith('x')]
    decoded_data = [each_split.tolist() for each_split in np.split(decoded_data, indicies) if len(each_split)]
    high_freq_data_lists = [[item.replace('x', '') for item in lst] for lst in decoded_data]
    high_freq_header = json.loads(settings.high_freq_header)
    high_freq_data = [dict(zip(high_freq_header, hf_list)) for hf_list in high_freq_data_lists]
    global prev_high_freq_data_path

    try:
        with open(prev_high_freq_data_path, 'rb') as f:
            num_newlines = 0
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while num_newlines < 2:  # 2 to seek to second last line, which is required due to empty row at end of data file
                    f.seek(-2, os.SEEK_CUR)
                    if f.read(1) == b'\n':
                        num_newlines += 1
            except OSError:
                f.seek(0)
            last_entry = f.readline().decode().strip("\r\n").split(",")
        prev_last_timestamp = last_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
    except Exception:
        pass

    try:
        with open(TEMP_HIGH_FREQ_DATA_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=high_freq_header)
            writer.writeheader()
            writer.writerows(high_freq_data)
        with open(TEMP_HIGH_FREQ_DATA_PATH, 'r') as f:
            f.readline()  # Read header to skip header
            first_entry = f.readline().strip("\r\n").split(",")
        initial_timestamp = first_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        with open(TEMP_HIGH_FREQ_DATA_PATH, 'rb') as f:
            num_newlines = 0
            try:  # catch OSError in case of a one line file
                f.seek(-2, os.SEEK_END)
                while num_newlines < 2:  # 2 to seek to second last line, which is required due to empty row at end of data file
                    f.seek(-2, os.SEEK_CUR)
                    if f.read(1) == b'\n':
                        num_newlines += 1
            except OSError:
                f.seek(0)
            last_entry = f.readline().decode().strip("\r\n").split(",")
        latest_timestamp = last_entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
        total_timestamp = f"{initial_timestamp}-{latest_timestamp}"
        output_filename = settings.output_high_freq_filename + ' %s.csv' % total_timestamp
        high_freq_data_path = os.path.join(OUTPUT_DIR, output_filename)
        os.rename(TEMP_HIGH_FREQ_DATA_PATH, high_freq_data_path)
    except Exception:
        return {"message": "There was an error uploading the file"}
    
    try:
        old_file_end_time = datetime.strptime(prev_last_timestamp, '%Y.%m.%d_%H.%M.%S.%f')
        new_file_start_time = datetime.strptime(initial_timestamp, '%Y.%m.%d_%H.%M.%S.%f')
        print(old_file_end_time, new_file_start_time)
    except Exception:
        print("error in timestamps")

    prev_high_freq_data_path = high_freq_data_path
    return {"message": "successfully uploaded high frequency data"}