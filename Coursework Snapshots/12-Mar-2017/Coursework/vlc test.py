#import vlc
#p = vlc.MediaPlayer(r"C:\Users\richa\OneDrive\Music\Animals\The Most Of The Animals\01-House Of The Rising Sun.mp3")
#p.play()
import sys
import time
from pygame import mixer
mixer.init()
print("loading")
mixer.music.load(r'C:\Users\richa\OneDrive\Music\ACDC\Black Ice\01 - Rock N Roll Train.mp3') # you may use .mp3 but support is limited
mixer.music.play()
time.sleep(10)
print("playing")

