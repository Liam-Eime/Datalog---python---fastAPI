from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    output_dir: str
    temp_low_freq_filename: str
    temp_high_freq_filename: str
    output_low_freq_filename: str
    output_high_freq_filename: str
    max_low_freq_data_rows: int
    scan_rate_micro_s: int
    low_freq_header: str
    high_freq_header: str
    model_config = SettingsConfigDict(env_file=".env")
