import src.vrc_controller as vrc
import io
from scipy.io.wavfile import write
import speech_recognition as sr

audio = vrc.Audio()
audio.initialize()

recognizer = sr.Recognizer()


@vrc.bus.on("audio_raw")
def audio_raw(data):
    wav_bytes = io.BytesIO()
    write(wav_bytes, 22050, data.astype("int32"))
    with sr.AudioFile(wav_bytes) as source:
        audio_data = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio_data)
            vrc.bus.emit("speech_heard", text)
        except sr.UnknownValueError:
            print("Could not fetch audio data")


@vrc.bus.on("speech_heard")
def event(text):
    print("Heard speech:", text)


vrc.loop_forever()
