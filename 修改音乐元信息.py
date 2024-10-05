import os
from mutagen.wave import WAVE
from dotenv import load_dotenv

load_dotenv()

# 打开 WAV 文件
ads = os.getenv('ICLOUD') + "/600_库/691_音乐/Adele/"
audio = WAVE(ads + "Adele-All I Ask.wav")

# 查看文件的所有元数据
print(audio.info.pprint())
