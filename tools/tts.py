# Озвучка текста: python3 tools/tts.py ГОЛОС СКОРОСТЬ "ТЕКСТ" файл.mp3
# Голоса: kk-KZ-AigulNeural, kk-KZ-DauletNeural, ru-RU-SvetlanaNeural, ru-RU-DmitryNeural
import sys, ssl, asyncio, edge_tts.communicate as c
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
c._SSL_CTX = ctx
voice, rate, text, out = sys.argv[1:5]
async def main():
    await c.Communicate(text, voice, rate=rate).save(out)
asyncio.run(main())
