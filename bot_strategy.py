import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileModifiedHandler(FileSystemEventHandler):
    def __init__(self, file_to_watch, script_to_run):
        super().__init__()
        self.file_to_watch = os.path.abspath(file_to_watch)
        self.script_to_run = script_to_run
        self.last_modified_time = time.time()  # Initialize the last modified time
        self.debounce_time = 60  # Time in seconds to wait before triggering the script

    def on_modified(self, event):
        if event.is_directory:
            return
        # Check if the modified file is the one you're watching
        if os.path.abspath(event.src_path) == self.file_to_watch:
            current_time = time.time()

            # Check if the modification happened after the debounce period
            if current_time - self.last_modified_time >= self.debounce_time:
                logging.info(f'{self.file_to_watch} has been modified!')
                self.last_modified_time = current_time  # Update last modified time

                # Start the Python script
                subprocess.run(["python3", self.script_to_run], check=True)

if __name__ == "__main__":
    file_to_watch = "percentages.txt"  # The file to monitor
    script_to_run = "strategy.py"  # The script to run when file is modified

    # Set up the event handler and observer
    event_handler = FileModifiedHandler(file_to_watch, script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    
    # Start watching
    observer.start()
    logging.info(f'Watching {file_to_watch} for modifications...')

    try:
        while True:
            time.sleep(10)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()

    observer.join()