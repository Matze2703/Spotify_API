# Spotify_API

Dieses Python-Programm zeigt den aktuell abgespielten Song auf Spotify an und ermöglicht die Steuerung (Play/Pause, Nächster, Vorheriger) über eine grafische Oberfläche mit Pygame. Die Hintergrundfarbe passt sich automatisch dem dominanten Farbton des Albumcovers an.

## Features

- Anzeige von Songtitel und Wiedergabegerät
- Fortschrittsbalken für den aktuellen Song
- Steuerung: Play/Pause, Nächster, Vorheriger Song (Premium benötigt)
- Dynamische Hintergrundfarbe basierend auf dem Albumcover

## Voraussetzungen

- Python 3.x
- [pygame](https://www.pygame.org/)
- [requests](https://docs.python-requests.org/en/latest/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [scikit-image](https://scikit-image.org/)
- Eigene Spotify-App mit Client-ID und Client-Secret

Installiere die benötigten Pakete mit:

```sh
pip install pygame requests opencv-python scikit-image
```

## Einrichtung

Beim ersten Start muss die vom Programm ausgegebene URL in einem Browser eingegeben werden und die App autorisiert werden. Nach der Autorisierung muss die zurückgegebene URL wieder ins Programm kopiert werden.