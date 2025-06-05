# file: auto_resize.py

import time
import os
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_FOLDER = "/var/www/pubg_tournament/src/static/uploads/logos"
TARGET_SIZE = (300, 300)  # الحجم لي بغيتي

class ImageResizeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            try:
                print(f"📸 Image detected: {event.src_path}")
                self.resize_image(event.src_path)
            except Exception as e:
                print(f"❌ Error resizing image: {e}")

    def resize_image(self, path):
        with Image.open(path) as img:
            img = img.convert("RGB")  # convert to safe format
            img.thumbnail(TARGET_SIZE)  # Resize while keeping ratio
            img.save(path, optimize=True, quality=85)
            print(f"✅ Resized and saved: {path}")

if __name__ == "__main__":
    event_handler = ImageResizeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCHED_FOLDER, recursive=False)
    observer.start()
    print(f"👀 Watching folder: {WATCHED_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()