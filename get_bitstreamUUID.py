from requests.exceptions import ConnectionError
from dspace_rest_client.client import DSpaceClient
import sys
import csv
import time

# Base URL for DSpace REST API
URL = "https://your-dspace-url/server/api"
USERNAME = "your_user_name"
PASSWORD = "your_password"
COLLECTION_UUID = "your_collection_UUID"
OUTPUT_CSV = "name_of_output.csv"

# Initialize client and authenticate
d = DSpaceClient(
    api_endpoint=URL, username=USERNAME, password=PASSWORD, fake_user_agent=True
)

authenticated = d.authenticate()

if not authenticated:
    print("Login failed.")
    sys.exit(1)
    
# Fetch all items using pagination
page = 0
size = 100  # Number of items per page; adjust if needed
all_results = []

# Search from DSpaceClient

while True:
    items = d.search_objects(query="*:*", scope=COLLECTION_UUID, dso_type="item", page=page, size=size)

    if not items:
        break

    for item in items:
        try:
            time.sleep(0.5)  # delay between calls
            bundles = d.get_bundles(parent=item)
        except ConnectionError as e:
            print(f"Connection error on item {item.uuid}, retrying...")
            time.sleep(3)
            try:
                bundles = d.get_bundles(parent=item)
            except Exception as err:
                print(f"Failed again on {item.uuid}: {err}")
                continue  

        for bundle in bundles:
            if bundle.name == "ORIGINAL":
                try:
                    time.sleep(0.5)
                    bitstreams = d.get_bitstreams(bundle=bundle)
                    if bitstreams:
                        all_results.append((item.uuid, bitstreams[0].uuid))
                except Exception as err:
                    print(f"Error fetching bitstream for {item.uuid}: {err}")
                break  

    page += 1
    
# Save to CSV
with open(OUTPUT_CSV, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Item UUID", "Bitstream UUID"])
    writer.writerows(all_results)

print(f"Saved {len(all_results)} item/bitstream UUID pairs to {OUTPUT_CSV}")
