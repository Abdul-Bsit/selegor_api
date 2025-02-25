import pandas as pd
import json
import os
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from fastapi.responses import FileResponse
from selegor_script import  run_scraper  # Correct import

app = FastAPI()

# Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to a specific domain if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

CSV_FILE = "Cleaned_Seloger_Properties.csv"
JSON_FILE = "Cleaned_Seloger_Properties.json"

# Function to convert CSV to JSON
def csv_to_json():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        json_data = df.to_dict(orient='records')
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Data converted to {JSON_FILE}")
    else:
        print("❌ CSV file not found!")

# Load JSON Data
def load_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI with CORS!"}

# Pagination Logic for Properties API
@app.get("/properties", response_model=List[Dict])
def get_properties(page: int = Query(1, description="Page number (1-based)")):
    if not os.path.exists("Cleaned_Seloger_Properties.json"):  # Check if data.json exists
        csv_to_json()  # Convert CSV to JSON only if JSON file doesn't exist
    data = load_json()
    page_size = 200  # Fetch 200 entries per request
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return data[start_idx:end_idx]

@app.get("/start-scraping")
def start_scraping(background_tasks: BackgroundTasks):
    # This function will now run in the background as intended
    background_tasks.add_task(run_scraper)  # Adjust according to your function
    return {"message": "Scraping started in the background!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
