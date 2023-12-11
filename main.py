"""
Python web application for a CR1000 data logger to send accelerometer and thermocouple data.

Uses FastAPI to build an API:
    Documentation: https://fastapi.tiangolo.com/
    Source Code: https://github.com/tiangolo/fastapi

Uses Uvicorn for running the Python web application:
    Documentation: https://www.uvicorn.org/

Author: Liam Eime
Date: 11/12/2023
"""

from fastapi import FastAPI, Request, Depends
from functools import lru_cache
from datetime import datetime, timedelta
import os
import csv
import json
import numpy as np
import pandas as pd

# .py file imports
import config
import timestamp
import files

low_freq_data_path = ''
prev_high_freq_data_path = ''

app = FastAPI()

@lru_cache
def get_settings():
    return config.Settings()
    
@app.post("/uploadLowFreq/{logger_filename}")
async def upload_low_freq_data(
    logger_filename: str, 
    request: Request,
    settings: config.Settings = Depends(get_settings)
):
    """
    #### HTTP Post method for the low frequency data

    This method receives low frequency data from the CR1000 data logger.\n
    The low frequency data is sent every 30s from the logger containing a single sample.\n
    The samples are appended to the same file until the desired amount of time has passes between initial and final sample, in which then a new file is written.\n
    Each sample has the following information:
        - 1 thermocouple temperature probe measuring temperature (1 measurement)
        - 2 tri-axial accelerometers measuring maximum and minimum accelerations for each axis (6 measurements each)
        - The timestamp for these samples

    ##### Parameters:
    - logger_filename: str
        - The incoming filename added to the http request by the CR1000 logger. Gets disregarded
    - request: Request
        - The incoming raw bytes of data as a http request
    - settings: config.Settings = Depends(get_settings)
        - Config settings linking the environment variables

    ##### Returns:
    - The http response message
    """
    PATH_TO_LOW_FREQ_FOLDER = os.path.join(settings.output_dir, settings.output_folder_low_freq)
    TEMP_LOW_FREQ_DATA_PATH = os.path.join(PATH_TO_LOW_FREQ_FOLDER, settings.temp_low_freq_filename) + ".csv"
    raw_bytes = await request.body()
    decoded_data = raw_bytes.decode("utf-8").strip("\r\n").replace('"', '').split(",")
    low_freq_header = json.loads(settings.low_freq_header)
    low_freq_data = dict(zip(low_freq_header, decoded_data))
    continue_with_file = True
    global low_freq_data_path
    try:  # try to open existing low freq data file
        with open(low_freq_data_path, 'r') as f:
            low_freq_data_rows_count = len(f.readlines())
        if low_freq_data_rows_count > settings.max_low_freq_data_rows:
            continue_with_file = False
    except Exception:
        pass  # pass, only errors when upload_low_freq_data() called for first time since server boot-up
    try:  # try to rename old file when row count reaches maximum row count
        if continue_with_file:
            os.rename(low_freq_data_path, TEMP_LOW_FREQ_DATA_PATH)
    except Exception:
        pass  # pass, only errors when attempting to rename non-existent file on first event
    try:  # try to open and append the low freq data to file and rename with total timestamp
        file_exists = os.path.exists(TEMP_LOW_FREQ_DATA_PATH)
        with open(TEMP_LOW_FREQ_DATA_PATH, 'a', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=low_freq_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(low_freq_data)
        initial_timestamp = timestamp.get_initial_timestamp(TEMP_LOW_FREQ_DATA_PATH)
        latest_timestamp = timestamp.get_final_timestamp(TEMP_LOW_FREQ_DATA_PATH, 1)
        low_freq_data_path = files.create_timestamped_filepath(initial_timestamp, latest_timestamp, settings.output_low_freq_filename, PATH_TO_LOW_FREQ_FOLDER)
        os.rename(TEMP_LOW_FREQ_DATA_PATH, low_freq_data_path)
    except Exception:  # exception returns an error message that there was an error updating file
        return {"message": "There was an error updating the file"}
    files.set_num_file_limit(PATH_TO_LOW_FREQ_FOLDER, settings.max_num_of_files)
    return {"message": "successfully uploaded low frequency data"}

@app.post("/uploadHighFreqAccel/{logger_filename}")
async def upload_high_freq_event(
    logger_filename: str,
    request: Request,
    settings: config.Settings = Depends(get_settings)
):
    """
    #### HTTP Post method for the high frequency acceleration data

    This method receives high frequency data from the CR1000 data logger.\n
    The high frequency data sent contains multiple rapid samples for an event in which accelerations go above a threshold.\n
    The multiple samples are all written to one file.\n
    The high frequency data samples contain the following:
        - Timestamps
        - 6 acceleration measurements (1 for each axis on 2 tri-axial accelerometers)

    ##### Parameters:
    - logger_filename: str
        - The incoming filename added to the http request by the CR1000 logger. Gets disregarded
    - request: Request
        - The incoming raw bytes of data as a http request
    - settings: config.Settings = Depends(get_settings)
        - Config settings linking the environment variables

    ##### Returns:
    - The http response message
    """
    PATH_TO_HIGH_FREQ_FOLDER = os.path.join(settings.output_dir, settings.output_folder_high_freq)
    TEMP_HIGH_FREQ_DATA_PATH = os.path.join(PATH_TO_HIGH_FREQ_FOLDER, settings.temp_high_freq_filename) + ".csv"
    raw_bytes = await request.body()
    decoded_data = raw_bytes.decode("utf-8").replace('"', '').replace('\r\n', 'x,').split(",")
    indicies = [(i+1) for i, x in enumerate(decoded_data) if x.endswith('x')]
    decoded_data = [each_split.tolist() for each_split in np.split(decoded_data, indicies) if len(each_split)]
    high_freq_data_lists = [[item.replace('x', '') for item in lst] for lst in decoded_data]
    high_freq_header = json.loads(settings.high_freq_header)
    high_freq_data = [dict(zip(high_freq_header, hf_list)) for hf_list in high_freq_data_lists]
    global prev_high_freq_data_path
    try:  # try to open and write the high freq data to file and rename with total timestamp
        with open(TEMP_HIGH_FREQ_DATA_PATH, 'w', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=high_freq_header)
            writer.writeheader()
            writer.writerows(high_freq_data)
        initial_timestamp = timestamp.get_initial_timestamp(TEMP_HIGH_FREQ_DATA_PATH)
        latest_timestamp = timestamp.get_final_timestamp(TEMP_HIGH_FREQ_DATA_PATH, 2)
        high_freq_data_path = files.create_timestamped_filepath(initial_timestamp, latest_timestamp, settings.output_high_freq_filename, PATH_TO_HIGH_FREQ_FOLDER)
        os.rename(TEMP_HIGH_FREQ_DATA_PATH, high_freq_data_path)
    except Exception:  # exception returns an error message that there was an error updating file
        return {"message": "There was an error updating the file"}
    try:  # try read the last timestamp from the previous high frequency data path
        prev_last_timestamp = timestamp.get_final_timestamp(prev_high_freq_data_path, 2)
    except Exception:
        pass  # pass, only errors when there is no previous high freq data file
    try:  # try combine current and previous files when current file is a continuation of previous one
        old_file_end_time = datetime.strptime(prev_last_timestamp, '%Y.%m.%d_%H.%M.%S.%f')
        new_file_start_time = datetime.strptime(initial_timestamp, '%Y.%m.%d_%H.%M.%S.%f')
        delta_time = new_file_start_time - old_file_end_time
        if delta_time <= timedelta(0, 0, settings.scan_rate_micro_s):
            combined_csv = pd.concat([pd.read_csv(prev_high_freq_data_path), pd.read_csv(high_freq_data_path)])
            temp_filename = os.path.join(PATH_TO_HIGH_FREQ_FOLDER, 'temp.csv')
            combined_csv.to_csv(temp_filename, index=False)
            os.remove(high_freq_data_path)
            os.remove(prev_high_freq_data_path)
    except Exception:
        pass  # pass, only errors when there is no previous file last timestamp
    try:  # try get total timestamp for new combined file
        temp_initial_timestamp = timestamp.get_initial_timestamp(temp_filename)
        temp_latest_timestamp = timestamp.get_final_timestamp(temp_filename, 2)
        high_freq_data_path = files.create_timestamped_filepath(temp_initial_timestamp, temp_latest_timestamp, settings.output_high_freq_filename, PATH_TO_HIGH_FREQ_FOLDER)
        os.rename(temp_filename, high_freq_data_path)
    except Exception:
        pass  # pass, only errors when there is no combined file made
    prev_high_freq_data_path = high_freq_data_path
    files.set_num_file_limit(PATH_TO_HIGH_FREQ_FOLDER, settings.max_num_of_files)
    return {"message": "successfully uploaded high frequency data"}