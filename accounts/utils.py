# accounts/utils.py
import requests

def get_cf_data(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    try:
        res = requests.get(url).json()
        if res["status"] == "OK":
            return res["result"][0]
    except Exception:
        return None
