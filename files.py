"""
Functions for handling files.
For use with the Python web application for CR1000 data logging.
Hard codes files as .csv along with main.py

Author: Liam Eime
Date: 08/12/2023
"""

import os

def set_num_file_limit(
    dir: str,
    max_num_of_files: int
):
    """
    #### Set a limit to the number of files allowed in the directory

    ##### Parameters:
    - dir: str
        - directory in which to set the file count limit 
    - max_num_of_files: int
        - number of files to limit directory to

    ##### Returns:
    - None
    """
    list_of_files = [os.path.abspath(name) for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    if len(list_of_files) > max_num_of_files:
        oldest_file = sorted([os.path.join(dir, f) for f in os.listdir(dir)], key=os.path.getctime)[0]
        os.remove(oldest_file)

def create_timestamped_filepath(
    initial_timestamp: str,
    final_timestamp: str,
    filename_to_timestamp: str,
    dir: str
):
    """
    #### Add timestamp to file and combine with directory to created timestamped file

    ##### Parameters:
    - initial_timestamp: str
        - formatted initial timestamp
    - final_timestamp: str
        - formatte final timestamp
    - filename_to_timestamp: str
        - filename to add timestamp to
    - dir: str
        - directory to join filename to make path

    ##### Returns:
        - new_path: str
            - path to timestamped file    
    """
    total_timestamp = f"{initial_timestamp}-{final_timestamp}"
    new_filename = filename_to_timestamp + ' %s.csv' % total_timestamp
    new_path = os.path.join(dir, new_filename)
    return new_path