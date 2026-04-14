import json
import urllib.request

url = 'http://127.0.0.1:8000/api/roadmap'
body = {
    "name": "Test User",
    "student_class": "B.Tech 2nd Year",
    "target_role": "Backend Engineer",
    "current_skills": ["Python", "Git"],
    "interests": ["APIs"]
}
req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    resp = urllib.request.urlopen(req)
    print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR:', e)
    try:
        import urllib.error
        if isinstance(e, urllib.error.HTTPError):
            body = e.read().decode('utf-8', errors='replace')
            print('HTTP ERROR BODY:', body)
    except Exception:
        pass
    try:
        import sys, traceback
        traceback.print_exc(file=sys.stdout)
    except Exception:
        pass
