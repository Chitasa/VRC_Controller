from .constants import SILENCE_THRESHOLD, MAX_SILENCE, MAX_AUDIO_LENGTH
import io
import numpy as np
from scipy.io.wavfile import write
from .singletons import bus
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr


class Audio:
    def __init__(self, audio_in: int | str = sd.default.device[0], audio_out: int | str = sd.default.device[1]):
        self.audio_in = audio_in
        self.audio_out = audio_out

        self.listener = AudioListener(audio_in)
        self.player = AudioPlayer(audio_out)

    def initialize(self):
        self.listener.initialize()

    def play_audio(self, audio: np.array, sample_rate: int = 22050):
        """
        Plays audio from numpy array
        """
        self.player.play_audio(audio, sample_rate)

    def play_file(self, file: str):
        """
        Plays audio from file
        """
        self.player.play_file(file)


class AudioListener:
    def __init__(self, audio_device: int | str = sd.default.device[0]):
        self.audio_device: str | int = audio_device
        self.stream: sd.InputStream | None = None

        self.running = False
        self.frames_passed = 0
        self.last_talked = 0
        self.temp_sounds = []
        self.last_talked_index = 0

    def initialize(self, audio_device: int | str = None):
        """
        Creates the stream
        """
        if self.stream is None or self.stream.closed:
            self.stream = sd.InputStream(device=audio_device if audio_device is not None else self.audio_device,
                                         callback=self.callback, samplerate=22050, dtype="int32")
            self.stream.start()

    def start_recording(self):
        """
        We captured sound -> start recording from here
        """
        if self.running:
            self.end_recording()

        self.running = True
        self.frames_passed = 0
        self.last_talked = 0
        self.temp_sounds = []
        self.last_talked_index = 0

    def end_recording(self):
        """
        We're cutting the recording off here
        """
        if self.running:
            self.running = False
            if (data := np.concatenate(self.temp_sounds[:self.last_talked_index])).size:
                bus.emit("audio_raw", data, threads=True)

    def callback(self, indata: np.array, frames: int, _, __):
        """
        sounddevice callback -> read more https://python-sounddevice.readthedocs.io/en/0.4.6/api/streams.html#sounddevice.InputStream
        """
        indata = np.mean(indata, axis=1)  # Converting 2 channels -> 1 channel
        rms = np.sqrt(np.mean(indata ** 2))  # Using Root Mean Squared to check for silence

        if not self.running:  # Start recording if not recording
            if rms > SILENCE_THRESHOLD:
                self.start_recording()
            else:
                return

        self.frames_passed += frames
        self.temp_sounds.append(indata.copy())

        if rms > SILENCE_THRESHOLD:
            self.last_talked = self.frames_passed
            self.last_talked_index = len(self.temp_sounds)  # Used to cut off silent bits

        if self.frames_passed > MAX_AUDIO_LENGTH * 22050 or \
                (self.frames_passed - self.last_talked) > MAX_SILENCE * 22050:
            self.end_recording()


class AudioPlayer:
    def __init__(self, audio_device: int | str = sd.default.device[0]):
        self.audio_device: str | int = audio_device

    def play_audio(self, audio: np.array, sample_rate: int = 22050):
        """
        Plays audio from numpy array
        """
        sd.play(audio, samplerate=sample_rate, device=self.audio_device)

    def play_file(self, file: str):
        """
        Plays audio from a file
        """
        data, fs = sf.read(file, dtype="float32")
        sd.play(data, samplerate=fs, device=self.audio_device)


def use_default_dictation():
    """
    Use https://pypi.org/project/SpeechRecognition/ & Google API to convert speech to text
    """
    recognizer = sr.Recognizer()

    @bus.on("audio_raw")
    def audio_raw(data: np.array):
        wav_bytes = io.BytesIO()
        write(wav_bytes, 22050, data.astype(np.int32))
        with sr.AudioFile(wav_bytes) as source:
            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                bus.emit("speech_heard", text)
            except sr.UnknownValueError:
                print("Could not fetch audio data")
