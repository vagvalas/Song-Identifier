import asyncio
import pyaudiowpatch as pyaudio
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from shazamio import Shazam
from PIL import Image, ImageTk
import io
import requests
import time
import wave

# Global variables
DURATION = 10  # Seconds to record
CHUNK_SIZE = 512
FILENAME = "loopback_record.wav"

class ShazamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shazam Identifier")
        self.root.geometry("400x350")

        self.devices = self.get_wasapi_loopback_devices()
        self.selected_device = tk.StringVar()
        self.selected_device.set(self.devices[0] if self.devices else "No devices found")

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Select Audio Source:").pack(pady=10)
        self.device_dropdown = ttk.Combobox(self.root, textvariable=self.selected_device, values=self.devices, state="readonly")
        self.device_dropdown.pack()

        self.recognize_button = ttk.Button(self.root, text="Recognize", command=self.start_recognition)
        self.recognize_button.pack(pady=20)

    def get_wasapi_loopback_devices(self):
        p = pyaudio.PyAudio()
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            p.terminate()
            return ["WASAPI not available"]
        
        devices = [p.get_device_info_by_index(i) for i in range(p.get_device_count())]
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                p.terminate()
                return ["No loopback device found"]
        
        p.terminate()
        return [default_speakers["name"]]

    def record_audio(self):
        p = pyaudio.PyAudio()
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            messagebox.showerror("Error", "WASAPI not available on this system!")
            p.terminate()
            return None
        
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                messagebox.showerror("Error", "Loopback device not found!")
                p.terminate()
                return None

        wave_file = wave.open(FILENAME, 'wb')
        wave_file.setnchannels(default_speakers["maxInputChannels"])
        wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(int(default_speakers["defaultSampleRate"]))
        
        def callback(in_data, frame_count, time_info, status):
            wave_file.writeframes(in_data)
            return (in_data, pyaudio.paContinue)
        
        with p.open(format=pyaudio.paInt16,
                    channels=default_speakers["maxInputChannels"],
                    rate=int(default_speakers["defaultSampleRate"]),
                    frames_per_buffer=CHUNK_SIZE,
                    input=True,
                    input_device_index=default_speakers["index"],
                    stream_callback=callback) as stream:
            time.sleep(DURATION)
        
        wave_file.close()
        p.terminate()
        
        with open(FILENAME, "rb") as f:
            audio_data = np.frombuffer(f.read(), dtype=np.int16)
        
        return audio_data

    async def recognize_song(self, audio_data):
        shazam = Shazam()
        result = await shazam.recognize(audio_data.tobytes())
        self.display_result(result)

    def start_recognition(self):
        audio_data = self.record_audio()
        if audio_data is not None:
            asyncio.run(self.recognize_song(audio_data))

    def display_result(self, result):
        if "track" in result:
            track = result["track"]
            name = track.get("title", "Unknown")
            artist = track.get("subtitle", "Unknown")
            album = track.get("sections", [{}])[0].get("metadata", [{}])[0].get("text", "Unknown")
            year = next((m["text"] for m in track.get("sections", [{}])[0].get("metadata", []) if "year" in m.get("title", "").lower()), "Unknown")
            image_url = track.get("images", {}).get("coverarthq", "")
            
            self.show_info_popup(name, artist, album, year, image_url)
        else:
            messagebox.showerror("Not Found", "No match found!")

    def show_info_popup(self, name, artist, album, year, image_url):
        popup = tk.Toplevel(self.root)
        popup.title("Song Identified")
        popup.geometry("300x400")

        ttk.Label(popup, text=f"Song: {name}").pack(pady=5)
        ttk.Label(popup, text=f"Artist: {artist}").pack(pady=5)
        ttk.Label(popup, text=f"Album: {album}").pack(pady=5)
        ttk.Label(popup, text=f"Year: {year}").pack(pady=5)
        
        if image_url:
            response = requests.get(image_url)
            img_data = response.content
            image = Image.open(io.BytesIO(img_data))
            image = image.resize((200, 200), Image.LANCZOS)
            img = ImageTk.PhotoImage(image)
            img_label = ttk.Label(popup, image=img)
            img_label.image = img
            img_label.pack(pady=10)

        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShazamApp(root)
    root.mainloop()