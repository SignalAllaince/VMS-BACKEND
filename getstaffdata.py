import requests
import json
import os
from dotenv import load_dotenv
def get_access_token(tenant_id, client_id, client_secret):
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": "https://graph.microsoft.com"
    }
    response = requests.post(token_url, data=payload)
    access_token = response.json().get('access_token') 
    return access_token

def get_all_users(access_token):
    graph_url = "https://graph.microsoft.com/v1.0"
    users_url = f"{graph_url}/users"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    all_users = []

    while True:
        response = requests.get(users_url, headers=headers)
        if response.status_code == 200:
            users_data = response.json().get('value', [])
            all_users.extend(users_data)

            next_link = response.json().get('@odata.nextLink')
            if not next_link:
                break  # No more pages to retrieve
            users_url = next_link
        else:
            print("Failed to retrieve user data.")
            break

    return all_users

def search_people(users, search_name):
    matching_users = []
    for user in users:
        display_name = user.get('displayName', '').lower()
        
        # List of titles to ignore
        ignore_titles = ["chairman", "mr", "mrs", "miss"]
        
        # Split the display name into words
        words = display_name.split()
        
        # Filter out words that are titles
        filtered_words = [word for word in words if word.lower() not in ignore_titles]
        
        # Join the remaining words to form the main name
        main_name = " ".join(filtered_words)
        
        if search_name.lower() in main_name:
            matching_users.append(user)
    return matching_users


def get_person_details(access_token, user_id):
    graph_url = "https://graph.microsoft.com/v1.0"
    user_url = f"{graph_url}/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(user_url, headers=headers)
    return response.json()

# def get_outlook_mail(access_token, user_id):
#     graph_url = "https://graph.microsoft.com/v1.0"
#     mail_url = f"{graph_url}/users/{user_id}/messages"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     response = requests.get(mail_url, headers=headers)
#     return response.json()
# @app.route('/name-endpoint')
load_dotenv()
def is_person_in_company(search_name):
    tenant_id = os.environ.get('TENANT_ID')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET') 
    # search_name = input("Enter the name or part of the name: ")

    access_token = get_access_token(tenant_id, client_id, client_secret)
    if access_token:
        all_users = get_all_users(access_token)
        matching_users = search_people(all_users, search_name)
        matching_users_data = []
        if matching_users:
            for person in matching_users[:10]:  # Limiting to the first ten results
                user_id = person['id']
                person_details = get_person_details(access_token, user_id)

                if person_details['jobTitle'] is None:
                    matching_users_data.append({
                                    "Full Name": person_details['displayName'],
                                    "Position": "Intern",
                                     "Email": person_details.get('userPrincipalName', 'N/A')})
                else:
                    matching_users_data.append({
                                    "Full Name": person_details['displayName'],
                                    "Position": person_details.get('jobTitle', 'N/A'),
                                     "Email": person_details.get('userPrincipalName', 'N/A')})
            return json.dumps(matching_users_data)
        else:
            return json.dumps("Sorry, i could not find anyone in this company by that name.")
    else:
        return json.dumps("Failed to obtain access token.")

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)