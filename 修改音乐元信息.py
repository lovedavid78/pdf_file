import os
from mutagen.wave import WAVE
from mutagen.id3 import ID3, TPE1, error
from dotenv import load_dotenv

load_dotenv()

# 打开 WAV 文件
ads = os.getenv('ICLOUD') + "/600_库/691_音乐/Adele/"
file_path = ads + "Adele-All I Ask.wav"

# 加载 WAV 文件
audio = WAVE(file_path)

# 尝试加载 ID3 标签，如果没有则创建一个新的
try:
    audio.add_tags()
except error:
    pass

# 添加艺术家信息
audio.tags.add(TPE1(encoding=3, text='Adele'))

# 保存更改
audio.save()