import requests
import json

ENDPOINTS = {
    "user-details":"https://api.spotify.com/v1/me",
    "play-history":"https://api.spotify.com/v1/me/player/recently-played"
}


def get_user_details(access_token):
    headers = {
        "Authorization": "Bearer " + access_token, 
        "Content-type": "application/x-www-form-urlencoded"
    }
    result = requests.get(ENDPOINTS['user-details'], headers=headers)
    return result.json()

def get_listening_history(access_token, cdc_time, limit=50):
    headers={"Authorization": "Bearer " + access_token}
    params={"after": str(cdc_time), "limit":str(limit)}
    result = requests.get(ENDPOINTS['play-history'], headers=headers, params=params)
    track_list = result.json()
    for item in track_list['items']:
        if 'available_markets' in item['track']: del item['track']['available_markets']
        if 'available_markets' in item['track']['album']: del item['track']['album']['available_markets']
    return track_list
    