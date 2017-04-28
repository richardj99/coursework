import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import sqlite3 as lite

conn=lite.connect('Music Library.db')
cur= conn.cursor()

library =str(input(r"please input directory:")) #string must be raw so that directory isn't interpreted as unicode
for dirName, subdirList, filelist in os.walk(library):
    for fname in filelist:
        if fname[-3:]  == ('mp3'): #validation for .mp3
            song_location = dirName + '\\' +fname
            song =EasyID3(song_location)
            length = MP3(song_location)
            print(length.info.length)

            song_name = str(song["title"])
            artist_name = str(song["artist"])
            #print(dirName+"\\"+fname )
            #print(song_name[2:-2])
            #Cprint(song_location)
            
