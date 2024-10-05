import os
from mutagen.wave import WAVE
from mutagen.id3 import ID3, TPE1, TIT2, TALB, error
from dotenv import load_dotenv
import musicbrainzngs

load_dotenv()

# 设置 MusicBrainz 用户代理
musicbrainzngs.set_useragent("fenghua", "1.0", "99930598@qq.com")

# 打开 WAV 文件
ads = os.getenv('ICLOUD') + "/600_库/691_音乐/Adele/"
file_path = ads + "Adele-All I Ask.wav"

# 提取文件名并去掉 'Adele-' 和 '.wav' 部分
file_name = os.path.basename(file_path)
title = file_name.replace('Adele-', '').replace('.wav', '')

# 加载 WAV 文件
audio = WAVE(file_path)

# 尝试加载 ID3 标签，如果没有则创建一个新的
try:
    audio.add_tags()
except error:
    pass

# 添加艺术家信息
audio.tags.add(TPE1(encoding=3, text='Adele'))

# 添加歌曲标题信息
audio.tags.add(TIT2(encoding=3, text=title))

# 查找专辑信息
result = musicbrainzngs.search_recordings(artist="Adele", recording=title, limit=1)
if result['recording-list']:
    album = result['recording-list'][0]['release-list'][0]['title']
    # 添加专辑信息
    audio.tags.add(TALB(encoding=3, text=album))

# 保存更改
audio.save()