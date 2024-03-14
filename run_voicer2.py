import threading
import time

import pyaudio
import pyautogui
import pyperclip
from pydub import AudioSegment
from pynput import mouse
from speechkit import configure_credentials, model_repository
from speechkit.common.utils import creds
from speechkit.stt import AudioProcessingType

from settings import yandex_secret


# Настройки потокового распознавания.
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 4096
RECORD_SECONDS = 120
WAVE_OUTPUT_FILENAME = "audio.wav"


# import keyboard as kbd
# keyboard = Controller()


class Voicer:

    def __init__(self, secret):
        self._secret = secret
        self._input_active = False
        self._is_running = False
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=secret
            )
        )
        self.client = model_repository.recognition_model()
        self.client.model = 'general'
        self.client.language = 'ru-RU'
        self.client.audio_processing_type = AudioProcessingType.Full

    def gen(self):
        # Задайте настройки распознавания.

        audio = pyaudio.PyAudio()
        # Начните запись голоса.
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        print("Listening...")
        pyperclip.copy('Слушаю...')
        pyautogui.hotkey("ctrl", "v")
        frames = []

        # Распознайте речь по порциям.
        latest_chunks = 0

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            if not self._input_active:
                latest_chunks += 1
            if not self._input_active and latest_chunks > 0:
                print('Input listen finished')
                self._is_running = False
                break


        print('Thinking....')
        pyperclip.copy('Думаю...')
        pyautogui.hotkey("ctrl", "v")
        # Остановите запись.
        stream.stop_stream()
        stream.close()
        audio.terminate()
        params = {
            "sample_width": audio.get_sample_size(FORMAT),
            "frame_rate": RATE,
            "data": b''.join(frames),
            "channels": CHANNELS
        }
        audio_segment = AudioSegment(**params)
        result = self.client.transcribe(audio_segment)
        # Using google to recognize audio
        res = result[0]
        return res.normalized_text

    def run_input(self):
        if self._is_running:
            return
        self._is_running = True
        print('Input listen started')
        text = self.gen()
        if text:
            pyautogui.hotkey("ctrl", "a")
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            pyperclip.copy(text)
        print('Finish')

    def monitor_input(self):
        print("Start monitor input")

        def on_click(x, y, button, pressed):
            if button.name == 'middle':
                self._input_active = pressed
                print(f"{pressed=}")
                if self._input_active:
                    threading.Thread(target=self.run_input).start()

        listener = mouse.Listener(on_click=on_click)
        listener.start()
        while True:
            time.sleep(50)
            pass


if __name__ == '__main__':
    voicer = Voicer(yandex_secret)
    voicer.monitor_input()
