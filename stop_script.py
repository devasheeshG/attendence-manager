import os
from shutil import copytree, rmtree
import time
import attendence_service as attendence_service
import logging
import datetime

logging.basicConfig(filename='logs/stop_script.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)

for process in attendence_service.run_service():
    process.join()
    logging.info(f'Attendence Service with ID {process} Stopped at {datetime.datetime.now()}')


source_folder = '/app'
dest_folder = '/coding-drive/attendence-manager/'
# Backbup database and logs
backup_folders = ['databases', 'logs']
# if os.path.exists(os.path.join(dest_folder, 'server_backup')):
#     rmtree(os.path.join(dest_folder, 'server_backup'))
    
for folder in backup_folders:
    rmtree(os.path.join(dest_folder, folder))
    copytree(os.path.join(source_folder, folder), os.path.join(dest_folder, folder))
    logging.info(f'Backed up {folder} at {datetime.datetime.now()}')

logging.info(f'Attendence Service Stopped at {datetime.datetime.now()}')
time.sleep(3)
