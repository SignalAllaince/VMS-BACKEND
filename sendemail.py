import requests
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_external_email(recipient_email, token):
    # Azure AD application information
    client_id = '085c948e-eb80-4e91-86cf-becf02d3c9f3'
    client_secret = 'fYZ8Q~irIFnPf_a9GsISvL9PQfB5rblZ-XWrzcxH'
    tenant_id = '47a5a918-b4ec-470f-86ca-c67e821ce45b'
    resource = 'https://graph.microsoft.com'  # Microsoft Graph API
    sender_email = 'unnamani@saconsulting.ai'
    # recipient_email = 'unnamani@saconsulting.ai'  # Replace with the recipient's email address

    # Request an access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': resource
    }

    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json().get('access_token')

    # Use the access token to make authenticated requests to Microsoft Graph API
    # Example: Send an email using Microsoft Graph API
    graph_api_url = f'https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail'

    # staff_name = "Uchenna Ikenna Nnamani"
    # visitor_name = "Ogonna Nnamani"
    # purpose_of_visit = "Delivery of laptop"
    #decode token
    payload = jwt.decode(token, 'mynameisslimshady', algorithms=['HS256'], options={"verify_exp": False})
    visitor_name = payload.get('visitor_name', '')
    staff_name = payload.get('staff_name', '')
    purpose_of_visit = payload.get('purpose_of_visit', '')
    # visitor_number = payload.get('visitor_number', '')
    selected_time = payload.get('selected_time', '')

    # Create the email message
    msg = MIMEMultipart()
    msg['Subject'] = f'Request for Visitation From {visitor_name}'
    # msg['From'] = sender_email  # Replace with the sender's email address
    msg['To'] = recipient_email
    body = f"Hello {visitor_name},\n\n{staff_name}, has accepted your visitation request to {purpose_of_visit} on {selected_time}.\n\n" \
           "You are to visit within the time frame of the time you chose\n\nRegards,\nAssistant Jason"
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using Microsoft Graph API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    email_data = {
        'message': {
            'subject': msg['Subject'],
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': recipient_email
                    }
                }
            ]
        }
    }

    response = requests.post(graph_api_url, headers=headers, json=email_data)

    if response.status_code == 202:
        print("Email sent successfully")
    else:
        print(f"Email could not be sent. Status Code: {response.status_code}")
        print(response.text)

def send_email(recipient_email, token):
    # Azure AD application information
    client_id = '085c948e-eb80-4e91-86cf-becf02d3c9f3'
    client_secret = 'fYZ8Q~irIFnPf_a9GsISvL9PQfB5rblZ-XWrzcxH'
    tenant_id = '47a5a918-b4ec-470f-86ca-c67e821ce45b'
    resource = 'https://graph.microsoft.com'  # Microsoft Graph API
    sender_email = 'unnamani@saconsulting.ai'
    # recipient_email = 'unnamani@saconsulting.ai'  # Replace with the recipient's email address

    # Request an access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': resource
    }

    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json().get('access_token')

    # Use the access token to make authenticated requests to Microsoft Graph API
    # Example: Send an email using Microsoft Graph API
    graph_api_url = f'https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail'

    # staff_name = "Uchenna Ikenna Nnamani"
    # visitor_name = "Ogonna Nnamani"
    # purpose_of_visit = "Delivery of laptop"
    #decode token
    payload = jwt.decode(token, 'mynameisslimshady', algorithms=['HS256'], options={"verify_exp": False})
    visitor_name = payload.get('visitor_name', '')
    staff_name = payload.get('staff_name', '')
    purpose_of_visit = payload.get('purpose_of_visit', '')
    # visitor_number = payload.get('visitor_number', '')
    selected_time = payload.get('selected_time', '')
    visitor_email = payload.get('visitor_email', '')

    # Create the email message
    msg = MIMEMultipart()
    msg['Subject'] = f'Request for Visitation From {visitor_name}'
    # msg['From'] = sender_email  # Replace with the sender's email address
    msg['To'] = recipient_email
    # Construct the links with the decoded details
    accept_link = f"http://127.0.0.1:5000/accept/{token}"
    reject_link = f"http://127.0.0.1:5000/reject/{token}"
    body = f"Hello {staff_name},\n\nA new visitor, {visitor_name}, is coming to visit for the purpose of {purpose_of_visit} on {selected_time}. Click the links below to accept or reject the visit:\n\n" \
           f"- [Accept Visit]({accept_link})\n" \
           f"- [Reject Visit]({reject_link})\n\nRegards,\nAssistant Jason"
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using Microsoft Graph API
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    email_data = {
        'message': {
            'subject': msg['Subject'],
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': recipient_email
                    }
                }
            ]
        }
    }

    response = requests.post(graph_api_url, headers=headers, json=email_data)

    if response.status_code == 202:
        print("Email sent successfully")
    else:
        print(f"Email could not be sent. Status Code: {response.status_code}")
        print(response.text)

# Call the function to send the email
# send_email()
