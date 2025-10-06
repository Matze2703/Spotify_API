import requests
import base64

client_id = "896914ef7b8247f6a6a34bb4be1eff98"
client_secret = "243d8606fa2f4da7a8e151798b1ce8bf"
redirect_uri = "http://127.0.0.1:3000/callback"
token_url = "https://accounts.spotify.com/api/token"

def getfreshtoken():

    # code muss über URL geholt werden:
    code_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri=http://127.0.0.1:3000/callback&scope=user-read-playback-state%20user-modify-playback-state%20user-read-currently-playing"
    print("\nPlease visit the following URL in your browser to authorize the application:")
    print(code_url)
    code = input("\nAfter authorization, paste the 'code' parameter from the redirect URL: ")


    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    response = requests.post(token_url, headers=headers, data=data)
    tokens = response.json()

    # Erfolg
    if response.status_code == 200:
        print(f"Access Token: {tokens['access_token']}")
        print(f"Refresh Token: {tokens['refresh_token']}")
        return tokens
    
    # Fehlschlag
    elif response.status_code == 400:
        print("\nThe code you submitted was used or is invalid, please try again:")
        print(code_url)
        code = input("\nAfter authorization, paste the 'code' parameter from the redirect URL: ")
    else:
        print("An Error occured, try again later")
    
    return None