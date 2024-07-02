from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class EventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            print(f'New file created: {file_path}')
            self.callback(file_name)