import webbrowser
from msal import ConfidentialClientApplication, PublicClientApplication

client_secret = 'fYZ8Q~irIFnPf_a9GsISvL9PQfB5rblZ-XWrzcxH'
app_id = '085c948e-eb80-4e91-86cf-becf02d3c9f3'

SCOPES = ['User.Read']

client = ConfidentialClientApplication(client_id=app_id, client_credential=client_secret)
authorization_url = client.get_authorization_request_url(SCOPES)
print(authorization_url)