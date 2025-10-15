import requests
import base64
import time
import json
import os
import get_tokens
import pygame
import cv2
import numpy as np
from skimage import io


# Prüfen, ob die Datei tokens.json existiert
# Falls nicht -> neue erstellen und refresh-token (+ access-token) anfordern
if not os.path.exists("tokens.json"):
    
    #tokens Programm abspielen
    tokens = get_tokens.getfreshtoken()
    
    # Tokens in JSON-Datei speichern
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)
    print("\nTokens erfolgreich geladen.")

#Tokens aus der Datei laden
with open("tokens.json", "r") as f:
    tokens = json.load(f)

refresh_token = tokens["refresh_token"]
access_token = tokens["access_token"]

# Spotify-App-Daten
client_id = "896914ef7b8247f6a6a34bb4be1eff98"
client_secret = "243d8606fa2f4da7a8e151798b1ce8bf"
redirect_uri = "http://127.0.0.1:3000/callback"
token_url = "https://accounts.spotify.com/api/token" # Spotify Token-Endpoint
url = "https://api.spotify.com/v1/me/player"         # Spotify Player


# ClientID + Secret Base64-kodieren
auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

response_headers = {
    "Authorization": f"Bearer {access_token}"
}

token_headers = {
    "Authorization": f"Basic {auth_header}",
    "Content-Type": "application/x-www-form-urlencoded"
}

token_body = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}



class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height+4), 0)
            
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isHovering(self, pos):
        # Pos is the mouse position or a tuple of (x, y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True        
        return False
    
# Define button colors
GRAY = (200, 200, 200)
PURPLE = (150, 0, 255)

# Create buttons
prev_btn = Button(GRAY, 40, 200, 80, 60, "<<")
play_pause_btn = Button(GRAY, 140, 200, 120, 60, "Play")
next_btn = Button(GRAY, 280, 200, 80, 60, ">>")


def send_spotify_command(command):
    if command == "play_pause":
        # Toggle play/pause
        if is_playing:
            response = requests.put("https://api.spotify.com/v1/me/player/pause", headers=response_headers)
        else:
            response = requests.put("https://api.spotify.com/v1/me/player/play", headers=response_headers)

    elif command == "next":
        response = requests.post("https://api.spotify.com/v1/me/player/next", headers=response_headers)
    elif command == "previous":
        response = requests.post("https://api.spotify.com/v1/me/player/previous", headers=response_headers)
    
    if response.status_code == 403:
        print("You need Premium for this feature")


# -- GUI --
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Player")

running = True

# temporäre Variablen zum init der GUI
progress_percent = 0 
is_playing = False
current_song = ""
current_device = ""
dominant_color = (0,0,0)

# --Main Loop--
while running:
    
    # -- API --
    try:
        response = requests.get(url, headers=response_headers)

        #OK
        if response.status_code == 200:
            response = response.json()
            with open("response.json","w") as file:
                json.dump(response, file)
            
            # Anzeige
            current_song = response['item']['name'] if response.get('item') else "Kein Song"
            current_device = response['device']['name'] if response.get('device') else "Kein Gerät"
            print(f"Now playing: {current_song} on {current_device}")
            progress_percent = int(response['progress_ms'] / response['item']['duration_ms'] * 100) if response.get('item') else 0
            print(f"{progress_percent}%")
            is_playing = response["is_playing"]  # Track play/pause state
            
            # Load album image and extract dominant color
            album_image = response['item']['album']['images'][0]['url']
            
            img = io.imread(album_image)
            if img.shape[-1] == 4:
                img = img[:, :, :3]  # Remove alpha channel if present

            pixels = np.float32(img.reshape(-1, 3))
            n_colors = 5
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            flags = cv2.KMEANS_RANDOM_CENTERS

            _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
            _, counts = np.unique(labels, return_counts=True)
            sorted_indices = np.argsort(-counts)
            dominant = palette[sorted_indices[0]]
            dominant_color = tuple(map(int, dominant))
            # If all dominant color RGB values are under 50, take the second dominant color
            if all(c < 50 for c in dominant_color) and len(sorted_indices) > 1:
                second_dominant = palette[sorted_indices[1]]
                dominant_color = tuple(map(int, second_dominant))


        elif response.status_code == 401:
            # Access Token mit Refresh Token aktualisieren
            token_response = requests.post(token_url, headers=token_headers, data=token_body)
            tokens = token_response.json()
            access_token = tokens["access_token"]
            print("Neues Access Token:", access_token)
            response_headers["Authorization"] = f"Bearer {access_token}"

        elif response.status_code == 204:
            print("Kein aktives Gerät oder keine Wiedergabe.")
        
        else:
            print("Fehler beim Refresh:", response.status_code, response.text)
        
    
    except requests.ConnectionError:
        print("Internetverbindung prüfen")

    time.sleep(0.1)

    # -- GUI --
    screen.fill(dominant_color)
    play_pause_btn.draw(screen)
    prev_btn.draw(screen)
    next_btn.draw(screen)

    # Fortschrittsbalken zeichnen
    bar_x = 50
    bar_y = 150
    bar_width = 300
    bar_height = 20
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), 2)  # Rahmen
    fill_width = int(bar_width * (progress_percent / 100))
    if is_playing:
        pygame.draw.rect(screen, (30, 215, 96), (bar_x, bar_y, fill_width, bar_height))  # Spotify-Grün wenn gerade abgespielt wird
    else:
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, fill_width, bar_height)) # Grau wenn pausiert

    # Songtitel und Gerät anzeigen
    font = pygame.font.SysFont('comicsans', 24)
    song_text = font.render(f"Song: {current_song}", True, (255, 255, 255))
    device_text = font.render(f"Gerät: {current_device}", True, (255, 255, 255))
    screen.blit(song_text, (50, 50))
    screen.blit(device_text, (50, 80))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if play_pause_btn.isHovering(pos):
                print("Play/Pause")
                send_spotify_command("play_pause")
                is_playing = not is_playing
            elif next_btn.isHovering(pos):
                print("Next")
                send_spotify_command("next")
            elif prev_btn.isHovering(pos):
                print("Previous")
                send_spotify_command("previous")
