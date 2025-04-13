import os
import time
from pathlib import Path
from typing import Optional
import base64
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
from ..services.consultant_service import ConsultantService
from ..models.chat import ChatMessage

class LogoAnalyzer:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.last_analyzed_file: Optional[str] = None
        self.last_analyzed_time: Optional[float] = None
        self.consultant_service = ConsultantService()
        
    def get_latest_image(self) -> Optional[str]:
        """Get the most recently added/modified image in the folder"""
        try:
            files = list(Path(self.folder_path).glob('*.png'))  # Assuming PNG format
            if not files:
                return None
            # Get the most recently modified file
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            return str(latest_file)
        except Exception as e:
            print(f"Error getting latest image: {e}")
            return None

    async def analyze_image(self, image_path: str) -> None:
        """Analyze the image using OpenAI through ConsultantService"""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            
            print(f"[{datetime.now()}] Analyzing image: {os.path.basename(image_path)}")
            
            # Call the consultant service
            response, _ = await self.consultant_service.get_chat_response(
                message="Please analyze this logo and provide detailed feedback about its design, including strengths and potential improvements.",
                chat_history=[],
                image_base64=encoded_string
            )
            
            print(f"Analysis result for {os.path.basename(image_path)}:")
            print(response)
            print("-" * 80)
            
            self.last_analyzed_file = image_path
            self.last_analyzed_time = time.time()
            
        except Exception as e:
            print(f"Error analyzing image: {e}")

class LogoChangeHandler(FileSystemEventHandler):
    def __init__(self, analyzer: LogoAnalyzer):
        self.analyzer = analyzer
        self.loop = asyncio.get_event_loop()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.png'):
            print(f"New image detected: {event.src_path}")
            # Run the async analysis in the event loop
            self.loop.create_task(self.analyzer.analyze_image(event.src_path))

async def start_logo_monitoring(folder_path: str, check_interval: int = 120):
    """
    Start monitoring the logo folder for changes
    folder_path: Path to the folder containing logo images
    check_interval: Interval in seconds to check for updates (default 2 minutes)
    """
    analyzer = LogoAnalyzer(folder_path)
    
    # Set up file system observer for immediate new file detection
    event_handler = LogoChangeHandler(analyzer)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    try:
        while True:
            # Check if it's time to re-analyze the latest image
            current_time = time.time()
            if (analyzer.last_analyzed_time is None or 
                current_time - analyzer.last_analyzed_time >= check_interval):
                
                latest_image = analyzer.get_latest_image()
                if latest_image and (latest_image != analyzer.last_analyzed_file or 
                                   analyzer.last_analyzed_time is None):
                    await analyzer.analyze_image(latest_image)
            
            await asyncio.sleep(1)  # Small sleep to prevent CPU overuse
            
    except KeyboardInterrupt:
        observer.stop()
        print("Monitoring stopped")
    finally:
        observer.join()

if __name__ == "__main__":
    folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fakedata")
    asyncio.run(start_logo_monitoring(folder_path)) 