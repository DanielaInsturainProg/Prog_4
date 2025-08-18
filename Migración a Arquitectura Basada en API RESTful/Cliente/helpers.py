import os, requests
from flask import flash

API_BASE = os.getenv("API_BASE_URL", "http://localhost:5001")

def api_request(method, path, json=None, timeout=8):
    url = f"{API_BASE}{path}"
    try:
        resp = requests.request(method, url, json=json, timeout=timeout)
        # Manejo de errores HTTP
        if resp.status_code >= 400:
            try:
                payload = resp.json()
            except Exception:
                payload = {"error": resp.text}
            return None, payload, resp.status_code
        # OK
        try:
            return resp.json(), None, resp.status_code
        except Exception:
            return None, {"error": "invalid JSON from API"}, 502
    except requests.Timeout:
        return None, {"error": "API timeout"}, 504
    except requests.ConnectionError:
        return None, {"error": "API unreachable"}, 503
    except Exception as e:
        return None, {"error": str(e)}, 500

def flash_api_error(payload, default="Error comunicándose con la API"):
    msg = payload.get("error") if isinstance(payload, dict) else None
    flash(msg or default, "danger")
