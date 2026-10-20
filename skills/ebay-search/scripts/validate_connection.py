#!/usr/bin/env python3
"""Validate eBay Browse API credentials without revealing secrets."""

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
REQUIRED_ENV = ("EBAY_APP_ID", "EBAY_CERT_ID")


def emit(payload, exit_code=0):
    print(json.dumps(payload))
    raise SystemExit(exit_code)


def main():
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name, "").strip()]
    if missing:
        emit(
            {
                "status": "not_configured",
                "missing": missing,
                "help": "Set non-empty EBAY_APP_ID and EBAY_CERT_ID environment variables.",
            },
            1,
        )

    client_id = os.environ["EBAY_APP_ID"].strip()
    client_secret = os.environ["EBAY_CERT_ID"].strip()
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    request = urllib.request.Request(
        OAUTH_URL,
        data=urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            }
        ).encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        status = "authentication_failed" if error.code in (400, 401, 403) else "connection_failed"
        emit({"status": status, "detail": f"eBay OAuth returned HTTP {error.code}."}, 1)
    except (OSError, TimeoutError) as error:
        emit({"status": "connection_failed", "detail": str(error)}, 1)
    except (UnicodeDecodeError, json.JSONDecodeError):
        emit(
            {
                "status": "connection_failed",
                "detail": "eBay OAuth returned an unreadable response.",
            },
            1,
        )

    if payload.get("access_token"):
        emit({"status": "ready", "detail": "eBay Browse API authentication succeeded."})

    emit(
        {
            "status": "authentication_failed",
            "detail": "eBay OAuth did not return an access token.",
        },
        1,
    )


if __name__ == "__main__":
    main()