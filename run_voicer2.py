import threading
import time

import pyaudio
import pyautogui
import pyperclip
from pydub import AudioSegment
from pynput import mouse, keyboard
from speechkit import configure_credentials, model_repository
from speechkit.common.utils import creds
from speechkit.stt import AudioProcessingType

from settings import yandex_secret

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 4096
RECORD_SECONDS = 120
WAVE_OUTPUT_FILENAME = "audio.wav"


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
        self.in_place = False

    def listen_audio(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        frames = []
        latest_chunks = 0
        print("Listening...")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            if not self._input_active:
                latest_chunks += 1
            if not self._input_active and latest_chunks > 0:
                print('Input listen finished')
                self._is_running = False
                break

        stream.stop_stream()
        stream.close()
        audio.terminate()
        sample_width = audio.get_sample_size(FORMAT)
        return {
            "frames": frames,
            "sample_width": sample_width
        }

    def transcribe(self, recorded_data: dict):
        print('Thinking....')
        data = b''.join(recorded_data["frames"])
        params = {
            "sample_width": recorded_data["sample_width"],
            "frame_rate": RATE,
            "data": data,
            "channels": CHANNELS
        }
        audio_segment = AudioSegment(**params)
        result = self.client.transcribe(audio_segment)
        res = result[0]
        return res.normalized_text

    def run_input(self):
        if self._is_running:
            return
        self._is_running = True
        print(f'Input listen started {self.in_place = }')
        if not self.in_place:
            pyperclip.copy('Слушаю...')
            pyautogui.hotkey("ctrl", "v")
        listening_data = self.listen_audio()
        if not self.in_place:
            pyperclip.copy('Думаю...')
            pyautogui.hotkey("ctrl", "v")
        text = self.transcribe(listening_data)
        if text:
            if self.in_place:
                pyautogui.press("delete")
            else:
                pyautogui.hotkey("ctrl", "a")
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            pyperclip.copy("")
        self.in_place = False
        print('Finish')

    def monitor_input(self):
        print("Start monitor input")

        def on_mouse_click(x, y, button, pressed):
            if button.name == 'middle':
                if pressed:
                    self._input_active = pressed
                    threading.Thread(target=self.run_input).start()
                else:
                    time.sleep(2)
                    self._input_active = pressed

        mouse_listener = mouse.Listener(on_click=on_mouse_click)
        mouse_listener.start()

        def key_board_press(key):
            if key == keyboard.Key.shift:
                print(f"Shift pressed in_place mode ON")
                self.in_place = True

        # def key_board_releases(key):
        #     if key == keyboard.Key.ctrl:
        #         self.ctr_pressed = False

        keyboard_listener = keyboard.Listener(
            on_press=key_board_press
        )
        keyboard_listener.start()

        while True:
            time.sleep(50)
            pass


if __name__ == '__main__':
    voicer = Voicer(yandex_secret)
    voicer.monitor_input()
