import certifi, asyncio, json, sys
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts
TEXT = ("Привет! Меня зовут Баян. "
"Я фотограф и эс-эм-эм специалист. А ещё человек, у которого в голове постоянно появляются новые идеи. "
"Я снимаю фото и видео, помогаю бизнесам вести социальные сети и запускаю рекламу. "
"Делюсь своими знаниями и обучаю тому, что люблю сама: съёмке и продвижению. "
"Моя жизнь — это съёмки, проекты, встречи, семья и планы, которые иногда меняются прямо посреди дня. "
"А когда хочется замедлиться, я беру книгу или готовлю что-нибудь вкусное. "
"Здесь будет про работу, обучение, личную жизнь, книги, готовку, мечты и мой путь. "
"Не знаю, куда он меня приведёт, но предлагаю пройти его вместе. "
"Подписывайся — будем знакомиться!")
async def main():
    c = edge_tts.Communicate(TEXT, "ru-RU-SvetlanaNeural", rate="+8%", boundary="WordBoundary")
    words=[]
    with open("build/voice.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append([ch["text"], ch["offset"]/1e7, (ch["offset"]+ch["duration"])/1e7])
    json.dump(words, open("build/words.json","w"), ensure_ascii=False)
    for i,w in enumerate(words): print(i, w[0], round(w[1],2), round(w[2],2))
asyncio.run(main())
