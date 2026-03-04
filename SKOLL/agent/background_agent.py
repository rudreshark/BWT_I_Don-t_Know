import os
import time
import base64
import io
import threading
import psutil
import pyautogui
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socketio

SERVER_URL = os.environ.get('SKOLL_SERVER', 'http://127.0.0.1:5000')
USER_ID = os.environ.get('SKOLL_USER_ID', '1')

sio = socketio.Client()

class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            payload = {
                'user_id': USER_ID,
                'process_name': 'file-system',
                'action': 'download',
                'file_name': os.path.basename(event.src_path)
            }
            try:
                requests.post(f'{SERVER_URL}/api/ai-score', json=payload, timeout=2)
            except Exception:
                pass

def screenshot_stream():
    while True:
        try:
            img = pyautogui.screenshot()
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            b64 = base64.b64encode(buf.getvalue()).decode('ascii')
            sio.emit('agent_screenshot', {'user_id': USER_ID, 'image_base64': b64})
        except Exception:
            pass
        time.sleep(0.5)

def system_monitor():
    while True:
        try:
            active = ''
            try:
                import win32gui
                active = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            except Exception:
                pass
            for p in psutil.process_iter(['name', 'cpu_percent']):
                data = {
                    'user_id': USER_ID,
                    'process_name': p.info.get('name') or '',
                    'cpu_usage': p.info.get('cpu_percent') or 0.0,
                    'window_title': active
                }
                try:
                    requests.post(f'{SERVER_URL}/api/system-log', json=data, timeout=2)
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(1.0)

def start_watchdog():
    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    handler = DownloadHandler()
    observer = Observer()
    observer.schedule(handler, downloads, recursive=True)
    observer.start()
    return observer

def main():
    sio.connect(SERVER_URL)
    sio.emit('agent_hello', {'user_id': USER_ID})
    observer = start_watchdog()
    try:
        threading.Thread(target=screenshot_stream, daemon=True).start()
        threading.Thread(target=system_monitor, daemon=True).start()
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
