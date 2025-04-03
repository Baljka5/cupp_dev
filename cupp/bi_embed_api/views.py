# powerbiapp/views.py
from django.shortcuts import render
import msal
import requests

# === Power BI болон Azure AD тохиргоо ===
TENANT_ID = "bde68a4a-a9ba-4b1a-97f5-46f3b9f8f8cc"
CLIENT_ID = "78e801e0-36f4-4de5-afec-158901d1db90"
CLIENT_SECRET = "NQn8Q~5gPR1O1jgdF~1ZIpe39ao676CKNwlbubQK"

WORKSPACE_ID = "4d87b3c5-60f3-4fe9-9ac3-e36a6e1501f8"
REPORT_ID = "64c4020a-841f-4e15-bf04-04aa1a663dc4"


def get_embed_token():
    import json

    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    scope = ["https://analysis.windows.net/powerbi/api/.default"]

    print("▶ Authenticating with Azure AD...")
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=authority
    )

    token_response = app.acquire_token_for_client(scopes=scope)
    print("✅ Token response:")
    print(json.dumps(token_response, indent=2))

    if "access_token" not in token_response:
        raise Exception("❌ Authentication failed: " + token_response.get("error_description", "No description"))

    access_token = token_response["access_token"]

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "accessLevel": "View"
        # Include "identities" here if RLS is used
    }

    print("▶ Sending embed token request to Power BI...")
    print(f"URL: {url}")
    print("Headers:")
    print(json.dumps(headers, indent=2))
    print("Payload:")
    print(json.dumps(data, indent=2))

    response = requests.post(url, headers=headers, json=data)

    print("🔄 Power BI API response:")
    print(f"Status Code: {response.status_code}")
    print("Response Text:")
    print(response.text)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to generate embed token: {response.status_code} - {response.text}")

    token = response.json().get("token")
    print("✅ Embed token successfully retrieved:")
    print(token)

    return token


def report_view(request):
    embed_token = get_embed_token()
    context = {
        'embed_token': embed_token,
        'report_id': REPORT_ID,
        'workspace_id': WORKSPACE_ID
    }
    return render(request, 'point/report.html', context)
