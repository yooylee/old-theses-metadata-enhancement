import os
import requests
import csv
import time

CSV_FILE = "name_of_your_file.csv" # where item UUID and bistream UUID generated from get_bitstreamUUID.py
OUTPUT_DIR = "path_to_your_director_to_save_PDFs"
BASE_URL = "https://your-dspace-url/server/api/core/bitstreams"

# os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        bitstream_uuid = row['Bitstream UUID'].strip()  # Adjust to match your CSV column
        download_url = f"{BASE_URL}/{bitstream_uuid}/content"

        try:
            response = requests.get(download_url, timeout=60)
            response.raise_for_status()

            # Save as PDF
            filename = os.path.join(OUTPUT_DIR, f"{bitstream_uuid}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Failed to download {bitstream_uuid}: {e}")
            
        time.sleep(1)  # Add delay to be kind to the server
