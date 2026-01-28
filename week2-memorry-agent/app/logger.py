import json
import time

def log_event(event: str, **kwargs):
    payload = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event": event,
        **kwargs
    }
    print(json.dumps(payload, ensure_ascii=False))