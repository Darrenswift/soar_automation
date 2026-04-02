# @title Bulk close cases
import requests
import logging
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configuration ---
api_key = "" # @param {"type":"string","placeholder":"11111-222-333-444-5555555"}
soar_hostname = "" # @param {"type":"string","placeholder":"mysoar.siemplify-soar.com"}
case_name_match = "" # @param {"type":"string","placeholder":""}
TIMEOUT = 10 # Seconds to wait for a server response

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# --- Resilient Session Setup ---
# A session reuses TCP connections, drastically speeding up bulk API calls.
session = requests.Session()

# Configure automatic retries for transient errors and connection timeouts
retry_strategy = Retry(
    total=3,  # Max number of retries per request
    backoff_factor=1,  # Wait 1s, 2s, then 4s between retries
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
    allowed_methods=["POST", "GET"] 
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# Apply headers to the entire session
session.headers.update({
    'content-type': 'application/json',
    'Appkey': api_key
})

# --- Prepare Timestamps ---
# Using timezone.utc is the modern Python standard over utcnow()
now_utc = datetime.now(timezone.utc)
end_time = now_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

# --- 1. Search for Cases ---
search_payload = {
    "startTime": "2023-07-10T00:00:00.000Z",
    "endTime": end_time,
    "isCaseClosed": False,
    "pageSize": 10000,
    "timeRangeFilter": 0,
    "sortBy": {
        "sortOrder": 0,
        "sortBy": "Id"
    }
}
search_endpoint = f'https://{soar_hostname}/api/external/v1/search/CaseSearchEverything'

try:
    logging.info("Searching for open cases...")
    # Using 'json=payload' automatically formats as JSON, replacing json.dumps()
    response = session.post(url=search_endpoint, json=search_payload, timeout=TIMEOUT)
    response.raise_for_status() # Raises an exception for HTTP errors (4xx, 5xx)
    json_results = response.json()
except requests.exceptions.RequestException as e:
    logging.error(f"Search request failed or timed out permanently: {e}")
    exit(1)

# Filter cases
cases_to_close = [
    case for case in json_results.get('results', []) 
    if case_name_match in case.get('title', '')
]

logging.info(f"Found {len(cases_to_close)} cases matching '{case_name_match}'. Starting closure process...")

# --- 2. Bulk Close Cases ---
close_endpoint = f'https://{soar_hostname}/api/external/v1/cases/CloseCase'

for case in cases_to_close:
    case_id = case['id']
    close_payload = {
        "caseId": case_id,
        "reason": "NotMalicious",
        "rootCause": "Lab test",
        "comment": "Closed with API automation",
    }
    
    try:
        # The session will automatically retry up to 3 times if it hits a timeout 
        # or server error before throwing a RequestException here.
        del_resp = session.post(url=close_endpoint, json=close_payload, timeout=TIMEOUT)
        del_resp.raise_for_status()
        logging.info(f"Successfully closed case {case_id}")
    except requests.exceptions.Timeout:
        logging.warning(f"Timeout occurred closing case {case_id} despite retries. Skipping to next.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to close case {case_id}. Error: {e}")

logging.info("Script execution complete.")
