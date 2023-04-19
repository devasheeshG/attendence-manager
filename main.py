import multiprocessing as mp
from shutil import copytree, ignore_patterns
import os
import datetime
import time
import logging
import subprocess

# Refresh all files except database
ignored_folders = ['databases', '.vscode', 'logs', 'capchas_examples', 'temp', '__pycache__', 'tools']
ignored_files = ['notebook.ipynb', 'Dockerfile', 'main.py']

source_folder = '/coding-drive/attendence-manager/'
destination_folder = r'/app/'

# if os.path.exists(destination_folder):
#     os.remove(destination_folder)
copytree(source_folder, destination_folder, ignore=ignore_patterns(*ignored_folders, *ignored_files), dirs_exist_ok=True)

# Make important folders
imp_folders = ['databases', 'logs', 'temp']
for folder in imp_folders:
    os.makedirs(os.path.join(destination_folder, folder), exist_ok=True)

logging.basicConfig(filename='logs/attendence_service.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

# Run app.py process
def run_app():
    logging.info(f'Running Streamlit App at {datetime.datetime.now()}')
    subprocess.run(['streamlit', 'run', 'app.py'])
mp.Process(target=run_app).start()

def attendence_service_runner():
    import attendence_service
    
    # Run at Startup of Container
    attendence_service.run_service()
    logging.info(f'Attendence Service Ran at Startup at {datetime.datetime.now()}')
    
    '''
    #! Schedule attendance_service
        - When Container is started -> DONE
        - 11 to 12 PM everyday
        - every 6 Hours
        - Force Refresh -> DONE
        - when attendance is exited -> STOP SCRIPT
    '''
    # Define the time ranges to run the command every day
    ranges = [
        (datetime.time(hour=22, minute=0), datetime.time(hour=0, minute=0)), # 10 PM to 12 AM
    ]

    # Define the time interval to run the command every 6 hours
    interval = datetime.timedelta(hours=1)

    while True:
        now = datetime.datetime.now().time()

        # Check if the current time falls within any of the defined ranges
        in_range = False
        for start, end in ranges:
            if start <= now < end:
                in_range = True
                break

        # Run the command if the current time falls within a range or is a multiple of the interval
        if in_range:
            attendence_service.run_service()
            logging.info(f'Attendence Service Ran at {datetime.datetime.now()}')

        # Wait for the specified interval before checking the time again
        time.sleep(interval.total_seconds())

mp.Process(target=attendence_service_runner).start()