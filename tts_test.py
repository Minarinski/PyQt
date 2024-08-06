import pyttsx3

def onEnd(name, completed):
    print(f"Finished speaking: {name}")

def speak_text(text):
    engine = pyttsx3.init()
    engine.connect('finished-utterance', onEnd)
    engine.say(text)
    engine.startLoop()

# 함수 호출
speak_text("안녕하세요, 이것은 테스트입니다.")
print("This will print immediately after calling speak_text()")
