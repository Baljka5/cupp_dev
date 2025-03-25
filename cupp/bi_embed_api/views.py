# # powerbiapp/views.py
# from django.shortcuts import render
# import msal
# import requests
#
# # ==== Azure болон Power BI тохиргоо ====
# TENANT_ID = "bde68a4a-a9ba-4b1a-97f5-46f3b9f8f8cc"
# CLIENT_ID = "78e801e0-36f4-4de5-afec-158901d1db90"
# CLIENT_SECRET = "NQn8Q~5gPR1O1jgdF~1ZIpe39ao676CKNwlbubQK"
#
# WORKSPACE_ID = "b55b6256-075e-4f32-9ab3-6c905a2f6efb"
# REPORT_ID = "64c4020a-841f-4e15-bf04-04aa1a663dc4"
#
#
# def get_embed_token():
#     authority = f"https://login.microsoftonline.com/{TENANT_ID}"
#     print(f"auth", authority)
#     scope = ["https://graph.microsoft.com/.default"]
#
#     app = msal.ConfidentialClientApplication(
#         CLIENT_ID,
#         authority=authority,
#         client_credential=CLIENT_SECRET
#     )
#
#     token_response = app.acquire_token_for_client(scopes=scope)
#     print(f"Token", token_response)
#     if "access_token" not in token_response:
#         raise Exception("❌ Authentication failed:", token_response.get("error_description"))
#
#     access_token = token_response["access_token"]
#
#     # Power BI Embed Token API
#     url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
#     print(f"URL", url)
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {access_token}"
#     }
#     data = {
#         "accessLevel": "View"
#     }
#
#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code != 200:
#         print("❌ ERROR", response.status_code, response.text)
#     response.raise_for_status()
#
#     embed_token = response.json().get("token")
#     return embed_token
#
#
# def report_view(request):
#     embed_token = get_embed_token()
#     context = {
#         'embed_token': embed_token,
#         'report_id': REPORT_ID,
#         'workspace_id': WORKSPACE_ID
#     }
#     return render(request, 'point/report.html', context)
