from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from datetime import datetime, date
import pandas as pd
from ocr import OCR
import sqlite3
import yaml
from yaml.loader import SafeLoader
import multiprocessing as mp
import logging
import os
import platform
import json

subjects = json.load(open("subjects.json", "r"))

def get_attendence(username: str, password: str) -> pd.DataFrame():

    options = Options()
    # Create the driver
    if platform.system() == "Windows":
        driver_path = 'tools/chromedriver.exe'
        options.binary_location = os.getenv("BRAVE_PATH", default=None)
    elif platform.system() == "Linux":
        driver_path = '/usr/bin/chromedriver'
        options.binary_location = '/usr/bin/google-chrome'
    else:
        raise Exception("Platform not supported")

    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(
        options=options,
        service=Service(
            executable_path=driver_path
        )
    )
    # Open the website
    driver.get('https://evarsity.srmist.edu.in/srmsip/')
    sleep(3)
    logging.info("Opened the website")

    while True:
        captcha_text = driver.find_element(
            by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[5]/td[1]/b[1]/div[1]")
        if captcha_text.text == "":
            logging.info("Captcha Found")

            # Username
            login_id = driver.find_element(
                by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/input[1]")
            login_id.send_keys(username)
            logging.info("Entered the username")

            # Password
            login_password = driver.find_element(
                by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/input[1]")
            login_password.send_keys(password)
            logging.info("Entered the password")

            # Captcha
            captcha = driver.find_element(
                by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[4]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/img[1]")
            captcha.screenshot(f"temp/capcha_{username}.png")
            capcha_code = OCR(f"temp/capcha_{username}.png")
            os.remove(f"temp/capcha_{username}.png")

            logging.info(f"Captcha code is: {capcha_code}")

            capcha_input = driver.find_element(
                by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[6]/td[1]/input[1]")
            capcha_input.send_keys(capcha_code)
            logging.info("Filled the captcha")

            # Login Button
            login_button = driver.find_element(
                by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[7]/td[1]/input[1]")
            login_button.click()
            logging.info("Clicked the login button")
            sleep(2)

            # Check for unsuccessful login
            # Case 1: Invalid Word Verification OR Invalid Username or Password
            try:
                error_msg = driver.find_element(
                    by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/form[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/p[1]/b[1]/font[1]")
                if error_msg.text != "":
                    logging.error("Invalid Username or Password")
                    driver.refresh()
                    sleep(3)
            except:
                logging.info(
                    "No such error message - Invalid Username or Password")

            # Case 2: Force Login
            try:
                force_login_btn = driver.find_element(
                    by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/table[1]/tbody[1]/tr[1]/td[2]/div[1]/div[1]/form[2]/table[1]/tbody[1]/tr[4]/td[1]/input[1]")
                force_login_btn.click()
                logging.warning("Forcing Login")
                sleep(2)
            except:
                logging.info("No such Button - Force Login")

            # Verify if the login was successful
            try:
                clg_name = driver.find_element(
                    by=By.XPATH, value="/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[3]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[8]/td[1]")
                if clg_name.text == "College: SRM Engineering College, Ghazhiabad":
                    logging.info("Login Successful")
                    sleep(2)
                    break
            except:
                logging.critical(
                    "Cannot find the college name - Login Unsuccessful")

            driver.refresh()
            sleep(3)

        else:
            # driver.close()
            logging.warning("Refreshing Page.. Captcha not loaded")
            driver.refresh()
            sleep(3)
            # return get_attendence(username, password)

    # Click on the Attendence link
    acadmic_btn = driver.find_element(
        By.XPATH, "/html[1]/body[1]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/table[1]/tbody[1]/tr[1]/td[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]/table[1]/tbody[1]/tr[1]/td[1]")
    hover = ActionChains(driver)
    hover.move_to_element(acadmic_btn).perform()
    sleep(2)
    attendence_btn = driver.find_element(
        By.XPATH, "//td[contains(text(), 'Attendance')]")
    attendence_btn.click()
    logging.info("Clicked on the Attendence link")
    sleep(2)

    # Get the attendence data
    table_data = driver.find_element(by=By.CLASS_NAME, value="hos")
    data = pd.read_html(table_data.get_attribute('outerHTML'))[0]
    data.columns = data.iloc[0]
    data.drop([0], inplace=True)
    data.drop(["Code", "OD/ML Percentage", "Average %",
              "Absent Hours", "Total Percentage"], axis=1, inplace=True)
    data = data[data['Description'] != 'TOTAL']
    data = data.rename(columns={'Description': 'Subject'})
    data = data.rename(columns={'Max. Hours': 'Total Classes'})
    data = data.rename(columns={'Att. Hours': 'Attended'})
    data.columns.name = None
    data.reset_index(drop=True, inplace=True)
    data.index = data.index + 1

    # Rename Subject Names
    for subject in subjects:
        data = data.replace(subject, subjects[subject])

    logging.shutdown()
    driver.close()
    return data

def attendence_service(username: str, password: str) -> None:
    # Create the logs folder if not exists
    if not os.path.exists("logs"):
        os.mkdir("logs")
    
    # Basic logging Config
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s',
                        handlers=[
                            logging.FileHandler(f"logs/{username}.log"),
                            logging.StreamHandler()
                        ]
                        )
    logging.info(f"----------------- {datetime.now()} : {username}-----------------")

    conn = sqlite3.connect(f'databases/{username}.sqlite')
    cur = conn.cursor()
    attendence_data = get_attendence(username, password)

    # Create the table if not exists
    for subject in attendence_data['Subject']:
        cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{subject}'")
        if cur.fetchone():
            logging.info(f"Table {subject} already exists")
        else:
            cur.execute(f"""CREATE TABLE IF NOT EXISTS "{subject}" (
                Date STRING PRIMARY KEY,
                Total_Classes INTEGER,
                Attended INTEGER,
                Absent INTEGER,
                Percentage REAL 
                )""")
            logging.info(f"Created the table {subject}")
            conn.commit()

    '''
    Points to Code Upon:
    1. If the data is already present, then update it
    2. If the data is not present, then insert it
    #! 3. Run this service 
            - When Container is started
            - 11 to 12 PM everyday
            - Force Refresh
    '''
    
    # Insert the data into the table
    for _, row in attendence_data.iterrows():
        # Insert the data into the table with date as the primary key
        # If the date is already present, then update the data
        # If the date is not present, then insert the data
        
        subject: str = str(row['Subject'])
        date_: str = str(date.today())   # YYYY-MM-DD
        total_classes: int = int(row['Total Classes'])
        attended: int = int(row['Attended'])
        absent: int = int(total_classes) - int(attended)
        precentage: float = round((attended / total_classes) * 100, 2)
        cur.execute(
            f"""
            INSERT INTO '{subject}' (Date, Total_Classes, Attended, Absent, Percentage) 
            VALUES ('{date_}', '{total_classes}', '{attended}', '{absent}', '{precentage}') 
            ON CONFLICT(Date) DO UPDATE SET
                Total_Classes = '{total_classes}',
                Attended = '{attended}',
                Absent = '{absent}',
                Percentage = '{precentage}'
            """
        )
        logging.info(f"Inserted the data for {subject} on {date_}")
        conn.commit()
    
def run_service() -> None:
    # Read the users file
    with open('users.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Get the users Credentials
    for user in config['credentials']['usernames']:
        evarsity_username = config['credentials']['usernames'][user]['evarsity_username']
        evarsity_password = config['credentials']['usernames'][user]['evarsity_password']

        # Start the attendence service threads for user
        mp.Process(target=attendence_service, args=(
            evarsity_username, evarsity_password)).start()
        
    return mp.active_children()

def refresh_user(username: str, password: str) -> None:
    attendence_service(username, password)
