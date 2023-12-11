"""
Functions for getting and formatting timestamps, for use for creating and naming the .csv data files.
For use with the Python web application for CR1000 data logging.

Author: Liam Eime
Date: 12/12/2023
"""

# Python imports
import os

def format_timestamp(entry: list[str]):
    """
    #### Format timestamp string for desired appearance in file

    ##### Parameters:
    - entry: list[str]
        - entry from csv file containing timestamp information

    ##### Returns:
    - formatted_timestamp: str
        - timestamp from entry formatted for file name
    """
    formatted_timestamp = entry[0].replace(':', '.').replace("-", ".").replace(" ", "_")
    return formatted_timestamp

def get_initial_timestamp(file_path: str):
    """
    #### Get the initial timestamp from file

    ##### Parameters:
    - file_path: str
        - string containing the path to the file from which to get the initial timestamp from

    ##### Returns:
    - initial_timestamp: str
        - formatted initial timestamp
    """
    with open(file_path, 'r') as f:
        f.readline()  # skip over the header
        first_entry = f.readline().strip("\r\n").split(",")
    initial_timestamp = format_timestamp(first_entry)
    return initial_timestamp

def get_final_timestamp(
    file_path: str, 
    row_pos: int
):
    """
    #### Get the final timestamp from file

    ##### Parameters:
    - file_path: str
        - string containing the path to the file from which to get the final timestamp from
    - row_pos: int
        - integer value indicating which row from last in file to get timestamp from, 1 means last row and 2 means second last row.

    ##### Returns:
    - final_timestamp: str
        - formatted final timestamp
    """
    num_newlines = 0
    with open(file_path, 'rb') as f:
        try:  # catch OSError in case of a one line file
            f.seek(-2, os.SEEK_END)
            while num_newlines < row_pos:
                f.seek(-2, os.SEEK_CUR)
                if f.read(1) == b'\n':
                    num_newlines += 1
        except OSError:
            f.seek(0)
        final_entry = f.readline().decode().strip("\r\n").split(",")
    final_timestamp = format_timestamp(final_entry)
    return final_timestamp