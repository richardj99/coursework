from mutagen.easyid3 import EasyID3
song = EasyID3(r"C:\Users\Richard\OneDrive\Music\A Day To Remember\Common courtesy\02 - Right back at it again.mp3")
artist = str(song["artist"])
print(song)

