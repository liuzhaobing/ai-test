import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

now_file_path = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.dirname(now_file_path)
LOG_PATH = os.path.join(BASE_PATH, 'logs')
os.makedirs(LOG_PATH, exist_ok=True)
