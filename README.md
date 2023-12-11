## Python web application for CR1000 data logger data retrieval
Python web application for a CR1000 data logger to send accelerometer and thermocouple data.\
Program also includes a plotting.py script to plot the data as it is received by the Python web application.

### FastAPI
Uses FastAPI to build an API:
* Documentation: https://fastapi.tiangolo.com/
* Source Code: https://github.com/tiangolo/fastapi

### Uvicorn
Uses Uvicorn for running the Python web application
* Documentation: https://www.uvicorn.org/

### Main
main.py must be run using uvicorn as a FastAPI application.

### Plotting
plotting.py can be run separately from main.py as a Python file, to plot the data as it is received by the web application running on main.py.

### Author and Date
Author: Liam Eime\
Date: 11/12/2023
