import csv
import logging
import os
import subprocess
import threading
import time
from datetime import datetime
from glob import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """ Utility function to run a shell command and return the output """
    return subprocess.run(["powershell", "-Command", command], capture_output=True, text=True).stdout.strip()

def find_chromedriver():
    user_cache_dir = os.path.join(os.getenv('USERPROFILE'), '.cache', 'selenium', 'chromedriver', 'win64')
    chromedriver_files = glob(os.path.join(user_cache_dir, '**', 'chromedriver.exe'), recursive=True)
    if chromedriver_files:
        return chromedriver_files[0]  # Return the first found path
    else:
        # If no ChromeDriver is found, use webdriver_manager to install it
        return ChromeDriverManager().install()

def find_paths():
    start_time = time.time()  # Start timer for chrome path retrieval

    # Default paths for Chrome and ChromeDriver
    default_chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    default_chromedriver_path = r"C:\Users\Miltiadis\.cache\selenium\chromedriver\win64\124.0.6367.91\chromedriver.exe"  # Adjust with your likely path

    if os.path.exists(default_chrome_path) and os.path.exists(default_chromedriver_path):
        logging.info("Using default paths for Chrome and ChromeDriver.")
        elapsed_time = time.time() - start_time
        logging.info(f"Time taken to confirm default paths: {elapsed_time:.2f} seconds")
        return default_chrome_path, default_chromedriver_path

    # PowerShell commands to find Chrome and ChromeDriver paths
    commands = [
        r"(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe').'(Default)'",
        r"(Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe').'(Default)'"
    ]
    results = []

    # Thread worker to run commands
    def command_worker(cmd):
        path = run_command(cmd)
        if path:
            results.append(path)

    threads = []
    for command in commands:
        thread = threading.Thread(target=command_worker, args=(command,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    chrome_path = results[0] if results else None
    chromedriver_path = default_chromedriver_path

    elapsed_time = time.time() - start_time
    logging.info(f"Total time taken to locate Chrome and ChromeDriver: {elapsed_time:.2f} seconds")

    if chrome_path:
        return chrome_path, chromedriver_path

    logging.error("Failed to locate Chrome and ChromeDriver using both default and PowerShell paths.")
    return None, None

def init_browser():
    chrome_path, chromedriver_path = find_paths()
    if chrome_path and chromedriver_path:
        chrome_options = Options()
        chrome_options.binary_location = chrome_path
        chrome_options.add_argument('--headless')  # Add this line to hide the browser window
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    else:
        logging.error("Chrome or ChromeDriver path not found, make sure both are installed.")
        return None

def perform_speed_test(driver):
    driver.get("https://fast.com")
    logging.info("Website loaded, starting the speed test...")
    
    progress = tqdm(total=100, desc="Testing Progress")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "speed-value")))  # Ensure the test completes
    
    for i in range(30):  # Assume 30 seconds sufficient for most of the details to be visible
        time.sleep(1)
        progress.update(100/60)
        logging.info(f"Running initial speed test phase: {i+1}/30 seconds elapsed")

    try:
        more_info = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "show-more-details-link")))
        more_info.click()
        logging.info("Retrieving additional details...")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "upload-value")))  # Wait for upload details to appear
        for i in range(20):
            time.sleep(1)  # Wait a bit longer for all elements to stabilize
            progress.update(100/60)
            logging.info(f"Fetching more data: {i+1}/20 seconds elapsed")
    except Exception as e:
        logging.error(f"Error retrieving additional details: {str(e)}")

    progress.close()

    try:
        results = {
            'download_speed': driver.find_element(By.ID, "speed-value").text,
            'download_units': driver.find_element(By.ID, "speed-units").text,
            'upload_speed': driver.find_element(By.ID, "upload-value").text,
            'upload_units': driver.find_element(By.ID, "upload-units").text,
            'latency': driver.find_element(By.ID, "latency-value").text,
            'latency_units': 'ms',  # Assuming ms is the standard unit for latency
            'bufferbloat': driver.find_element(By.ID, "bufferbloat-value").text,
            'bufferbloat_units': 'ms'
        }
        logging.info("Speed Test completed successfully.")
        return results
    except NoSuchElementException:
        logging.error("One or more elements were not found on the page.")
        return None

def save_to_csv(data):
    if data is None:
        logging.error("No data to save.")
        return

    timestamp = datetime.now().isoformat().replace(':', '-')
    filename = f"{timestamp}_fast.com.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Metric', 'Value', 'Units'])
        # Use specific keys for metrics and their units
        metrics = [
            ('download_speed', 'download_units'),
            ('upload_speed', 'upload_units'),
            ('latency', 'latency_units'),
            ('bufferbloat', 'bufferbloat_units')
        ]
        for metric, units in metrics:
            if metric in data and units in data:
                writer.writerow([metric.replace('_', ' ').capitalize(), data[metric], data[units]])
            else:
                logging.warning(f"Data for {metric} or {units} not found.")
    logging.info(f"Results saved to CSV file: {filename}")

def main():
    driver = init_browser()
    if driver:
        results = perform_speed_test(driver)
        save_to_csv(results)
        driver.quit()
    else:
        logging.error("Webdriver could not be initialized.")

if __name__ == "__main__":
    main()
