import requests
import base64
import time
import json
import os
import get_tokens

#tokens Programm abspielen
print("\nPlease visit the following URL in your browser to authorize the application:")

# Prüfen, ob die Datei tokens.json existiert
if os.path.exists("tokens.json"):
    try:
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        print("Tokens erfolgreich geladen.")
    except json.JSONDecodeError:
        print("Fehler beim Laden der Tokens. Neue Tokens werden angefordert.")
        tokens = None

# Falls keine Tokens vorhanden sind -> neue erstellen
while not tokens:
    print("Keine gültigen Tokens vorhanden. Fordere neue Tokens an...")
    tokens = get_tokens.getfreshtoken()

    # Tokens in JSON-Datei speichern
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)
    print("Tokens gespeichert:", tokens)



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
  #  "refresh_token": 'AQAo8SfBk49-17O-FN6EfLA9BCdvpRmCAzMlAUrJCt_jeBVRhjlT6LhcJm7GiKqkxpGwUr_ZcFuttTcQf1Xfu37WFXeQ0PEFl1th5XbWop4HP7KncQkBauWgCoWPI2xQ12Q'
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
