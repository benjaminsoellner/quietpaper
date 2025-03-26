#!/usr/bin/env python3

import requests, json

auth = requests.post(
    "https://login.tado.com/oauth2/device_authorize",
    params=dict(
        client_id="1bb50063-6b0c-4d11-bd99-387f4a91cc46",
        scope="offline_access",
    )
).json()

print(f"""
    This tool sets up authentication to the smart-thermostat api tado.
    Navigate to {auth['verification_uri_complete']} and complete the authentication flow.
    For more information see: https://support.tado.com/en/articles/8565472-how-do-i-authenticate-to-access-the-rest-api
""")

input("After completing above steps press enter to continue, Ctrl+C to skip or abort....")
token = requests.post(
    "https://login.tado.com/oauth2/token",
    params=dict(
        client_id="1bb50063-6b0c-4d11-bd99-387f4a91cc46",
        device_code=auth['device_code'],
        grant_type="urn:ietf:params:oauth:grant-type:device_code",
    )
).json()

with open("secret/tado-refresh-token.json", "w") as f:
    json.dump(token, f)
