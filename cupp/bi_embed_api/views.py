from django.shortcuts import render, redirect
from django.conf import settings
import msal
import requests
import json

# === Azure болон Power BI тохиргоо ===
TENANT_ID = "bde68a4a-a9ba-4b1a-97f5-46f3b9f8f8cc"
CLIENT_ID = "78e801e0-36f4-4de5-afec-158901d1db90"
CLIENT_SECRET = "NQn8Q~5gPR1O1jgdF~1ZIpe39ao676CKNwlbubQK"
REDIRECT_URI = "https://pp.cumongol.mn/getAToken"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default", "openid", "profile", "offline_access"]

WORKSPACE_ID = "b55b6256-075e-4f32-9ab3-6c905a2f6efb"
REPORT_ID = "64c4020a-841f-4e15-bf04-04aa1a663dc4"


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )


def refresh_user_permissions(access_token):
    url = "https://api.powerbi.com/v1.0/myorg/datasets/refreshUserPermissions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print("▶ Calling RefreshUserPermissions...")
    response = requests.post(url, headers=headers)
    print("Status:", response.status_code)
    print(response.text)

    if response.status_code != 200:
        raise Exception("❌ Failed to refresh user permissions")


def get_dataset_id(access_token):
    url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to get dataset ID")
    return response.json().get("datasetId")


def generate_embed_token(access_token, dataset_id, username=None, rls_role=None):
    url = "https://api.powerbi.com/v1.0/myorg/GenerateToken"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "datasets": [{"id": dataset_id}],
        "reports": [{"id": REPORT_ID}],
        "targetWorkspaces": [{"id": WORKSPACE_ID}],
        "accessLevel": "View"
    }

    if username and rls_role:
        data["identities"] = [{
            "username": username,
            "roles": [rls_role],
            "datasets": [dataset_id]
        }]

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to generate embed token: {response.status_code} - {response.text}")

    return response.json().get("token")


# === Step 1: Login redirect ===
REQUEST_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]
AUTH_SCOPES = ["https://analysis.windows.net/powerbi/api/.default"]


# LOGIN REDIRECT VIEW
def login(request):
    auth_app = build_msal_app()
    auth_url = auth_app.get_authorization_request_url(
        scopes=REQUEST_SCOPES,  # ✅ reserved scopes байхгүй
        redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)


# CALLBACK VIEW (after user logs in)
def callback(request):
    code = request.GET.get("code", None)
    if not code:
        return render(request, "error.html", {"message": "Authorization code missing."})

    auth_app = build_msal_app()
    result = auth_app.acquire_token_by_authorization_code(
        code=code,
        scopes=AUTH_SCOPES,  # ✅ зөв scopes
        redirect_uri=REDIRECT_URI
    )

    if "access_token" not in result:
        return render(request, "error.html", {"message": "Token acquisition failed."})

    request.session["access_token"] = result["access_token"]
    request.session["id_token_claims"] = result.get("id_token_claims", {})
    return redirect("powerbi_report")


# === Step 3: Report view ===
def report_view(request):
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect("powerbi_login")

    # Optional: get logged-in user email for RLS if needed
    user_email = request.session.get("id_token_claims", {}).get("preferred_username")

    # Step 3A: Refresh user permissions
    refresh_user_permissions(access_token)

    # Step 3B: Get dataset ID
    dataset_id = get_dataset_id(access_token)

    # Step 3C: Generate embed token (with optional RLS)
    embed_token = generate_embed_token(access_token, dataset_id, username=user_email, rls_role="SalesRegion")

    context = {
        "embed_token": embed_token,
        "report_id": REPORT_ID,
        "workspace_id": WORKSPACE_ID
    }
    return render(request, "point/report.html", context)
