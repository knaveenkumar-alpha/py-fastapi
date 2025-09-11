from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from dotenv import load_dotenv

import logging
import requests
import time
import os

load_dotenv()  # take variables from .env


# ---------------- Logging Setup ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------- FastAPI App ---------------- #
app = FastAPI()

# ---------------- GHL Config ---------------- #
import os

# ---------------- GHL Config ---------------- #
GHL_ENDPOINT = "https://rest.gohighlevel.com/v1/contacts/"
GHL_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6InVpYjdiNlprTWdkbkh2elpCQ2wyIiwiY29tcGFueV9pZCI6Ik5LRzZKc0ZlUHJDdmxSaXhoeEZ2IiwidmVyc2lvbiI6MSwiaWF0IjoxNzAwMDgwNjE3MTU0LCJzdWIiOiJ1c2VyX2lkIn0.OLfjCBSGK1gCtsz4svrGnCugebXvWXsrA4k-JpUkYgM"


# ---------------- Retry Helper ---------------- #
def perform_ghl_request_with_retries(url, json_data, headers, retries=3, backoff_factor=2):
    """Send POST request with retries and exponential backoff"""
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=json_data, headers=headers, timeout=10)

            if response.status_code in (200, 201):
                return response  # Success
            else:
                logger.warning(
                    f"GHL API attempt {attempt} failed with status {response.status_code}: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"GHL API attempt {attempt} failed due to exception: {e}")

        # Wait before retry (exponential backoff)
        if attempt < retries:
            sleep_time = backoff_factor ** attempt
            logger.info(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

    raise Exception(f"Failed after {retries} attempts to contact GHL API")


# ---------------- API Endpoints ---------------- #
@app.post("/forward-ghl")
async def forward_payload(request: Request):
    try:
        # 1. Extract payload
        payload = await request.json()
        logger.info(f"Received payload: {payload}")

        # 2. Headers for GHL API
        headers = {
            "Authorization": f"Bearer {GHL_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

        # 3. Make request to GHL with retry
        ghl_response = perform_ghl_request_with_retries(GHL_ENDPOINT, payload, headers)

        # 4. Log & Return response
        logger.info(f"GHL Response: {ghl_response.status_code} {ghl_response.text}")

        return JSONResponse(
            status_code=ghl_response.status_code,
            content={
                "ghl_status_code": ghl_response.status_code,
                "ghl_response": ghl_response.json() if ghl_response.content else {}
            }
        )

    except Exception as e:
        logger.exception("Unexpected error occurred while forwarding payload")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/")
async def root():
    return {"message": "FastAPI → GHL forwarder is running with retries & logging!"}
