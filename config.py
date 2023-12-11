"""
Python class for storing the config settings.

Author: Liam Eime
Date: 11/12/2023
"""


# import libraries
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    output_dir: str
    output_folder_low_freq: str
    output_folder_high_freq: str
    temp_low_freq_filename: str
    temp_high_freq_filename: str
    output_low_freq_filename: str
    output_high_freq_filename: str
    max_low_freq_data_rows: int
    max_num_of_files: int
    scan_rate_micro_s: int
    low_freq_header: str
    high_freq_header: str
    model_config = SettingsConfigDict(env_file=".env")
