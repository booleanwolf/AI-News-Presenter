import os
import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
import importlib.util

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("news-processing-api")

# Import our modules dynamically
def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import the modules we created
try:
    news_scraper = import_module_from_file("news_scraper", "news_scraper.py")
    news_summarizer = import_module_from_file("news_summarizer", "news_summarizer.py")
    text_to_speech = import_module_from_file("text_to_speech", "text_to_speech.py")
except Exception as e:
    logger.error(f"Failed to import modules: {e}")
    raise

app = FastAPI(
    title="News Processing API",
    description="API for scraping, summarizing, and converting news to speech",
    version="1.0.0"
)

class ProcessingStatus(BaseModel):
    status: str
    message: str
    details: Optional[dict] = None

@app.get("/", response_model=ProcessingStatus)
async def root():
    return {
        "status": "success",
        "message": "News Processing API is running",
        "details": {
            "endpoints": [
                "/scrape-news",
                "/summarize",
                "/text-to-speech",
                "/process-all"
            ]
        }
    }

@app.post("/scrape-news", response_model=ProcessingStatus)
async def scrape_news(background_tasks: BackgroundTasks):
    def run_scraper():
        try:
            news_scraper.main()
            logger.info("News scraping completed.")
            return True
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return False

    background_tasks.add_task(run_scraper)
    
    return {
        "status": "processing",
        "message": "News scraping started in the background",
        "details": {
            "output_file": "news_articles.txt",
            "check_status": "GET /status/scraping"
        }
    }

@app.post("/summarize", response_model=ProcessingStatus)
async def summarize(background_tasks: BackgroundTasks):
    def run_summarizer():
        try:
            output_file = news_summarizer.main()
            return output_file is not None
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return False

    background_tasks.add_task(run_summarizer)
    
    return {
        "status": "processing",
        "message": "Summarization process started in the background",
        "details": {
            "check_status": "GET /status/summarizing"
        }
    }

@app.post("/text-to-speech", response_model=ProcessingStatus)
async def convert_to_speech(background_tasks: BackgroundTasks):
    def run_text_to_speech():
        try:
            output_file = text_to_speech.main()
            return output_file is not None
        except Exception as e:
            logger.error(f"Error during text-to-speech conversion: {e}")
            return False

    background_tasks.add_task(run_text_to_speech)
    
    return {
        "status": "processing",
        "message": "Text-to-speech conversion started in the background",
        "details": {
            "check_status": "GET /status/speech-conversion"
        }
    }

@app.post("/process-all", response_model=ProcessingStatus)
async def process_all(background_tasks: BackgroundTasks):
    def run_pipeline():
        try:
            # Step 1: Scrape news
            logger.info("Starting news collection...")
            news_scraper.main()
            
            # Step 2: Summarize content
            logger.info("Starting summarization...")
            summary_file = news_summarizer.main()
            if not summary_file:
                logger.warning("Summarization failed.")
                return False
                
            # Step 3: Convert to speech
            logger.info("Starting text-to-speech conversion...")
            audio_file = text_to_speech.main()
            if not audio_file:
                logger.warning("Text-to-speech conversion failed.")
                return False
                
            logger.info("Full pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during pipeline execution: {e}")
            return False

    background_tasks.add_task(run_pipeline)
    
    return {
        "status": "processing",
        "message": "Full processing pipeline started in the background",
        "details": {
            "check_status": "GET /status/pipeline"
        }
    }

@app.get("/download/{file_type}")
async def download_latest_file(file_type: str):
    """
    Download the most recently generated file of the specified type
    file_type options: articles, summaries, audio
    """
    # Define patterns for each file type
    patterns = {
        "articles": "news_articles",
        "summaries": "news_summaries_",
        "audio": "news_audio_"
    }
    
    if file_type not in patterns:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Choose from: {', '.join(patterns.keys())}")
    
    # Find the most recent file of the requested type
    matching_files = [f for f in os.listdir() if f.startswith(patterns[file_type])]
    if not matching_files:
        raise HTTPException(status_code=404, detail=f"No {file_type} files found")
    
    # Get the most recent file
    latest_file = max(matching_files, key=os.path.getctime)
    
    # Return the file
    return FileResponse(
        path=latest_file,
        filename=latest_file,
        media_type="application/octet-stream"
    )

@app.get("/status/{task}")
async def check_status(task: str):
    """
    Check the status of a background task.
    This is a placeholder implementation - in a real application, you would track
    task status in a database or similar.
    """
    # Mock implementation - would be replaced with actual status tracking
    valid_tasks = ["scraping", "summarizing", "speech-conversion", "pipeline"]
    
    if task not in valid_tasks:
        raise HTTPException(status_code=400, detail=f"Invalid task. Choose from: {', '.join(valid_tasks)}")
    
    # In a real implementation, you would fetch the actual status
    # For this example, we'll just return a generic response
    return {
        "status": "completed",  # or "in_progress", "failed", etc.
        "task": task,
        "completed_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)