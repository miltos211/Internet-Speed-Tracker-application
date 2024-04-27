import csv
import logging
from datetime import datetime
from tqdm import tqdm
from speedtest import Speedtest  # Import Speedtest library

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def perform_speed_test():
    st = Speedtest()
    st.download()
    st.upload()
    result_dict = st.results.dict()
    return result_dict

def save_to_csv(data):
    if data is None:
        logging.error("No data to save.")
        return

    timestamp = datetime.now().isoformat().replace(':', '-')
    filename = f"{timestamp}_speedtest.csv"
    logging.info(f"Saving results to CSV file: {filename}")

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Metric', 'Value', 'Units'])
        
        # Define the metrics we want to include and their corresponding keys in the data dictionary
        metrics_mapping = {
            'Download speed': 'download',
            'Upload speed': 'upload',
            'Latency': 'ping',
            'Server': None  # Exclude server information
        }

        # Initialize tqdm progress bar
        progress = tqdm(metrics_mapping.items(), desc="Saving Progress", total=len(metrics_mapping), unit='metric')

        for metric, key in progress:
            if key in data:
                if key == 'Server':
                    # Exclude server information
                    continue
                value = data[key]
                if 'speed' in metric:
                    # Convert from bits per second (bps) to Mbps and round to nearest integer
                    value = round(value / 1000000)  # Convert from bps to Mbps and round
                elif metric == 'Latency':
                    # Round latency to one decimal place
                    value = round(value, 1)
                units = 'Mbps' if 'speed' in metric else 'ms'
                writer.writerow([metric, value, units])
                logging.info(f"Saved {metric}: {value} {units}")
            else:
                logging.warning(f"Data for {metric} not found.")

    logging.info(f"Results saved to CSV file: {filename}")

def main():
    try:
        data = perform_speed_test()
        save_to_csv(data)
    except Exception as e:
        logging.error(f"An error occurred during the speed test: {str(e)}")

if __name__ == "__main__":
    main()
