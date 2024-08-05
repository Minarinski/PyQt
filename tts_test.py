from gtts import gTTS
import playsound

text = "318번 버스가 진입중입니다. 한걸음 뒤로 물러서주세요."

tts = gTTS(text=text, lang='ko')

tts.save("output.mp3")

playsound.playsound("output.mp3")