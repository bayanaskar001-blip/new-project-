import certifi, asyncio, json, sys
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts
TEXT = ("Привет! Меня зовут Баян. "
"Я фотограф, эс-эм-эм специалист и человек, у которого в голове всегда миллион идей. "
"Я снимаю фото и видео, помогаю бизнесам развивать свои страницы и запускаю рекламу. "
"А ещё обучаю других тому, что умею сама. "
"Мне нравится создавать, пробовать новое и наблюдать, как из маленькой идеи постепенно рождается что-то большое. "
"Но моя жизнь — это не только работа. Я люблю читать книги, готовить что-нибудь вкусное и находить время для близких. "
"В этом блоге я хочу делиться всем, что меня вдохновляет: работой, обычными днями, мыслями, мечтами и новыми начинаниями. "
"Честно? Я пока не знаю, к чему всё это приведёт. "
"Но мне интересно узнать!")
async def main():
    c = edge_tts.Communicate(TEXT, "ru-RU-SvetlanaNeural", rate="+14%", pitch="+18Hz", boundary="WordBoundary")
    words=[]
    with open("voice.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append([ch["text"], ch["offset"]/1e7, (ch["offset"]+ch["duration"])/1e7])
    json.dump(words, open("words.json","w"), ensure_ascii=False)
    for i,w in enumerate(words): print(i, w[0], round(w[1],2), round(w[2],2))
asyncio.run(main())
