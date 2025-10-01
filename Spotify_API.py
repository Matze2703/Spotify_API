import requests
import base64
import time
import json

# Deine Spotify-App-Daten
client_id = "896914ef7b8247f6a6a34bb4be1eff98"
client_secret = "243d8606fa2f4da7a8e151798b1ce8bf"
redirect_uri = "http://127.0.0.1:3000/callback"
access_token = "A"


token_url = "https://accounts.spotify.com/api/token" # Spotify Token-Endpoint
url = "https://api.spotify.com/v1/me/player"         # Spotify Player


# ClientID + Secret Base64-kodieren
auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

token_headers = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/x-www-form-urlencoded"
}

response_headers = {
    "Authorization": f"Bearer {access_token}"
}

data = {
    "grant_type": "refresh_token",
    "refresh_token": 'AQBgGo_Coo-0HaTnwH1hOBhTqxVl6tehqp6whT3DvlDgYC0W0EgLjLNx5tW5g1EoG7mdKofzgBtNylX6JOIB7Zb04WD_dliC0PplkY1psCYA_LQL0r783UAjWiXHOUJCpvU'
}


# --Main Loop--

while True:

    response = requests.get(url, headers=response_headers)

    if response.status_code == 200:     #OK
        response = response.json()
        with open("response.json","w") as file:
            json.dump(response, file)
        
        # Anzeige
        print(f"Now playing: {response['item']['name']} on {response['device']['name']}")
        progress_percent = int(response['progress_ms'] / response['item']['duration_ms'] * 100)
        print(f"{progress_percent}%")

    elif response.status_code == 401:
        # Access Token mit Refresh Token aktualisieren
        token_response = requests.post(token_url, headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }, data=data)
        token_response = requests.post(token_url, headers=token_headers, data=data)
        tokens = token_response.json()
        access_token = tokens["access_token"]
        print("Neues Access Token:", access_token)
        response_headers["Authorization"] = f"Bearer {access_token}"

    elif response.status_code == 204:
        print("Kein aktives Gerät oder keine Wiedergabe.")
        time.sleep(60)
    
    else:
        print("Fehler beim Refresh:", response.status_code, response.text)
    
    time.sleep(1)
