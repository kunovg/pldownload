import os
from pydub import AudioSegment, effects

files = os.listdir(os.getcwd())
for file in files:
    if ".m3u" not in file:
        print file
        song = AudioSegment.from_mp3(file)
        song = effects.normalize(song)
        song += 10
        song.export(file, format="mp3")
