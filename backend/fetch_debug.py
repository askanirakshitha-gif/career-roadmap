import json, urllib.request
print(json.loads(urllib.request.urlopen('http://127.0.0.1:8000/debug/anthropic_status').read().decode()))
