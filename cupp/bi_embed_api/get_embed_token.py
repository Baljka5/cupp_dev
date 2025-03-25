# get_embed_token.py
import msal
import requests
import json

# --- Тохиргоо ---
TENANT_ID = "d5b21b28-7ff0-49e2-858f-bbfb99efd267"
CLIENT_ID = "NQn8Q~5gPR1O1jgdF~1ZIpe39ao676CKNwlbubQK"
CLIENT_SECRET = "bde68a4a-a9ba-4b1a-97f5-46f3b9f8f8cc"

WORKSPACE_ID = "your-workspace-id"
REPORT_ID = "your-report-id"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# --- Access Token авах ---
app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)
token_response = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" not in token_response:
    print("❌ Authentication failed")
    exit()

ACCESS_TOKEN = token_response["access_token"]
print("✅ Access Token авсан")

# --- Embed Token авах ---
url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}
data = {
    "accessLevel": "View"
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    embed_token = response.json().get("token")
    print("✅ Embed Token:", embed_token)
    # HTML-д ашиглах гэж хадгална
    with open("embed_token.json", "w") as f:
        json.dump({
            "embedToken": embed_token,
            "reportId": REPORT_ID,
            "workspaceId": WORKSPACE_ID
        }, f)
else:
    print("❌ Embed Token авахад алдаа:", response.text)
