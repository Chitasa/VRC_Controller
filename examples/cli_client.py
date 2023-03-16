import src.vrc_controller as vrc

audio = vrc.Audio()
audio.initialize()
vrc.use_default_dictation()

orc = vrc.BotController()


@vrc.bus.on("speech_heard")
def event(text):
    print("Heard speech:", text)


def load_text(text):
    for i in text:
        if i == "True" or i == "False":
            yield i == "True"
        elif i.isdigit():
            yield int(i)
        else:
            yield i


while True:
    a = input().split()

    func = getattr(orc, a[0], None)
    if callable(func):
        func(*load_text(a[1:]))
    else:
        orc.send_message(" ".join(a))
