# Монтаж видео (Reels, YouTube, таргет)

Инструменты:
- **Python 3** — язык для скриптов монтажа
- **FFmpeg** — резка, склейка, зум, музыка, экспорт
- **faster-whisper** — распознавание речи (субтитры, поиск «эээ» и пауз)
- **Remotion** (папка `remotion/`) — анимированные субтитры и графика
- **yt-dlp** — загрузка видео по ссылке

Установка (делается автоматически в начале сессии):
```
pip3 install --break-system-packages -r requirements.txt
cd remotion && npm install
```
