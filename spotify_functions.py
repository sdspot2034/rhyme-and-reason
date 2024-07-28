import requests
import json

ENDPOINTS = {
    "user-details":"https://api.spotify.com/v1/me"
}


def get_user_details(access_token):
    headers = {
        "Authorization": "Bearer " + access_token, 
        "Content-type": "application/x-www-form-urlencoded"
    }
    result = requests.get(ENDPOINTS['user-details'], headers=headers)
    return json.loads(result.content)