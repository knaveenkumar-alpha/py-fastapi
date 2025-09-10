from fastapi import FastAPI, Request
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI is running on Azure App Service!"}

@app.post("/echo")
async def echo(request: Request):
    body = await request.json()
    logging.info(f"Received input: {body}")
    return {"received_data": body}
