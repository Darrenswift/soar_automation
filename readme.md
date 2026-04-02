# SOAR Bulk Case Closer

A resilient Python script designed to search for open cases in Siemplify / Google SecOps SOAR and close them in bulk based on a matching case title. 

This script is optimized for handling a large number of cases and network instability by utilizing connection pooling, automatic retries, and exponential backoff.

## Features

* **Efficient Bulk Operations:** Uses `requests.Session()` to keep the underlying TCP connection alive, drastically speeding up API calls compared to opening a new connection for every request.
* **Automatic Retries:** Configured with a retry strategy that automatically backs off and attempts the request again if it encounters temporary server errors (e.g., 502, 503, 504) or rate limits (429).
* **Explicit Timeouts:** Prevents the script from hanging indefinitely if the SOAR server becomes unresponsive.
* **Graceful Error Handling:** If a specific case fails to close, the script logs the error and safely continues processing the remaining cases.

## Disclaimer

Please test this script in a development or lab environment before running it in production. Bulk closing cases is a destructive action that cannot be easily undone. Ensure your case_name_match is specific enough that you do not accidentally close legitimate security incidents.

## Prerequisites

* Python 3.6 or higher
* `requests` library

You can install the required library using pip:

```bash
pip install requests

# --- Configuration ---
api_key = "YOUR_API_KEY_HERE" # Your SOAR AppKey
soar_hostname = "your-instance.siemplify-soar.com" # Your SOAR hostname (without https://)
case_name_match = "SecOps Connector" # The exact string to search for in case titles

python3 bulk_close_soar_cases.py

```


