import os
from mutagen.wave import WAVE
from mutagen.id3 import ID3, TPE1, TIT2, TALB, error
from dotenv import load_dotenv
import musicbrainzngs

load_dotenv()

# Set MusicBrainz user agent
musicbrainzngs.set_useragent("fenghua", "1.0", "99930598@qq.com")

# Open WAV file
ads = os.getenv('ICLOUD') + "/600_库/691_音乐/Adele/"
file_path = ads + "Adele-All I Ask.wav"

# Extract filename and remove 'Adele-' and '.wav' parts
file_name = os.path.basename(file_path)
title = file_name.replace('Adele-', '').replace('.wav', '')

# Load WAV file
audio = WAVE(file_path)

# Try to load ID3 tags, if they already exist, continue
try:
    audio.add_tags()
except error as e:
    if str(e) != "an ID3 tag already exists":
        raise

# Add artist information
audio.tags.add(TPE1(encoding=3, text='Adele'))

# Add song title information
audio.tags.add(TIT2(encoding=3, text=title))

# Search for album information
result = musicbrainzngs.search_recordings(artist="Adele", recording=title, limit=1)
if result['recording-list']:
    album = result['recording-list'][0]['release-list'][0]['title']
    # Add album information
    audio.tags.add(TALB(encoding=3, text=album))

# Save changes
audio.save()