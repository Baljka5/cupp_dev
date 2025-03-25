import msal

# Azure AD аппын мэдээлэл
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
TENANT_ID = "your-tenant-id"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]  # Хэрэглэгчийн эрх

# MSAL апп үүсгэх
app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

# Access token авах
token_response = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" in token_response:
    ACCESS_TOKEN = token_response["access_token"]
    print("✅ Access Token:", ACCESS_TOKEN)
else:
    print("❌ Authentication failed:", token_response.get("error_description"))
