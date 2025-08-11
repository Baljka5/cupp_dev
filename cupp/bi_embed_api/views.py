from django.shortcuts import render, redirect
from django.conf import settings
import msal
import requests

# === Azure болон Power BI тохиргоо ===
TENANT_ID = "bde68a4a-a9ba-4b1a-97f5-46f3b9f8f8cc"
CLIENT_ID = "78e801e0-36f4-4de5-afec-158901d1db90"
CLIENT_SECRET = "NQn8Q~5gPR1O1jgdF~1ZIpe39ao676CKNwlbubQK"
REDIRECT_URI = "https://pp.cumongol.mn/getAToken"

WORKSPACE_ID = "b55b6256-075e-4f32-9ab3-6c905a2f6efb"
REPORT_ID = "64c4020a-841f-4e15-bf04-04aa1a663dc4"
DATASET_ID = "8727efde-38ca-4a9f-9a0c-dc941621297e"

# === Scopes
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
AUTH_SCOPES = SCOPE


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )


def generate_embed_token(access_token, dataset_id, user_email=None, role=None):
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

    # Хэрэв RLS тохиргоо байгаа бол нэмнэ
    # if user_email and role:
    #     data["identities"] = [{
    #         "username": user_email,
    #         "roles": [role],
    #         "datasets": [dataset_id]
    #     }]

    response = requests.post(url, headers=headers, json=data)
    print("🔒 Embed Token Response:", response.status_code, response.text)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to generate embed token: {response.status_code} - {response.text}")

    return response.json().get("token")


# === STEP 1: Login redirect ===
def login(request):
    app = build_msal_app()
    auth_url = app.get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)


# === STEP 2: Callback view ===
def callback(request):
    code = request.GET.get("code", None)
    if not code:
        return render(request, "error.html", {"message": "Authorization code missing."})

    app = build_msal_app()
    result = app.acquire_token_by_authorization_code(
        code=code,
        scopes=AUTH_SCOPES,
        redirect_uri=REDIRECT_URI
    )

    print("🪪 Token Response:", result)

    if "access_token" not in result:
        return render(request, "error.html", {"message": "Token acquisition failed."})

    request.session["access_token"] = result["access_token"]
    request.session["id_token_claims"] = result.get("id_token_claims", {})
    return redirect("powerbi_report")


# === STEP 3: Show embedded report ===
def report_view(request):
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect("powerbi_login")

    user_email = request.session.get("id_token_claims", {}).get("preferred_username")
    role = "SalesRegion"

    embed_token = generate_embed_token(access_token, DATASET_ID, user_email, role)

    context = {
        "embed_token": embed_token,
        "report_id": REPORT_ID,
        "workspace_id": WORKSPACE_ID
    }
    return render(request, "point/report.html", context)
