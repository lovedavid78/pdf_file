import os
from mutagen.wave import WAVE
from mutagen.id3 import ID3, TPE1, TIT2, TALB, TDRC, error
from dotenv import load_dotenv
import musicbrainzngs

load_dotenv()

# Set MusicBrainz user agent
musicbrainzngs.set_useragent("fenghua", "1.0", "99930598@qq.com")

# Directory containing WAV files
directory = os.getenv('ICLOUD') + "/600_库/691_音乐/Adele/"

# Iterate over all files in the directory
for file_name in os.listdir(directory):
    if file_name.endswith('.wav'):
        file_path = os.path.join(directory, file_name)
        title = file_name.replace('Adele-', '').replace('.wav', '')

        # Load WAV file
        audio = WAVE(file_path)

        # Check if ID3 tags exist, if not, add them
        if audio.tags is None:
            audio.add_tags()

        tags = audio.tags

        # Add or update artist information
        tags.add(TPE1(encoding=3, text='Adele'))

        # Add or update song title information
        tags.add(TIT2(encoding=3, text=title))

        # Search for album information
        result = musicbrainzngs.search_recordings(artist="Adele", recording=title, limit=1)
        if result['recording-list']:
            album = result['recording-list'][0]['release-list'][0]['title']
            date = result['recording-list'][0]['release-list'][0]['date']
            # Add or update album information
            # tags.add(TALB(encoding=3, text=album))
            # Add or update date information
            # tags.add(TDRC(encoding=3, text=date))

        # Save changes
        audio.save()