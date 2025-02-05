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
import threading
import webbrowser
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk
import os
import sys
import ffmpeg
from io import BytesIO
from pydub import AudioSegment

# Global variables
DURATION = 4  # Seconds to record
CHUNK_SIZE = 512
#FILENAME = "loopback_record.wav"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ShazamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Song Identifier")
        self.root.geometry("450x400")
        self.root.iconbitmap(resource_path("icon.ico"))

        # Fetch and categorize audio devices
        self.loopback_devices, self.default_device = self.get_audio_devices()

        # Initialize the Tkinter variable for the selected device
        self.selected_device = tk.StringVar(value="Select a device")
        
        # Create UI widgets
        self.create_widgets()
        #self.load_animation(resource_path("shaza_anim.gif"))  # Load the animation frames
        # Set default device if it's available in the loopback list
        if any(device[0] == self.default_device for device in self.loopback_devices):
            self.selected_device.set(self.default_device)
        elif self.loopback_devices:
            # Set the fallback to the name of the first loopback device
            self.selected_device.set(self.loopback_devices[0][0])  # Access the first element's name
    

    def create_widgets(self):
        label = ttk.Label(self.root, text="Select Audio Source:")
        label.pack(pady=10)

        # Prepare device list with separators for categories
        loopback_device_names = [device[0] for device in self.loopback_devices]  # Extract names from loopback devices

        # Combine the lists with headers for each category
        device_list = ["---LOOPBACK DEVICES---"] + loopback_device_names

        self.device_dropdown = ttk.Combobox(self.root, textvariable=self.selected_device, values=device_list, state="readonly", width=60)
        self.device_dropdown.pack()


        # Bind the selection event to validate_selection to handle updates
        self.device_dropdown.bind("<<ComboboxSelected>>", self.selected_device.set(self.device_dropdown.get()))

        original_image = Image.open(resource_path("shaza_logo.png"))
        resized_image = original_image.resize((200, 200), Image.Resampling.LANCZOS)
        self.shazam_logo = ImageTk.PhotoImage(resized_image)
        
        self.recognize_button = ttk.Button(self.root, text="Recognize", command=self.start_recognition)
        self.recognize_button.pack(pady=20)

    def get_device_index_by_name(self, device_name):
        for device in self.loopback_devices:
            if device[0] == device_name:  # Compare the name
                return device[1]  # Return the index
        return None  # Return None if not found

    # Note: In 'get_audio_devices', ensure 'default_device_name' is correctly identified and appended with '[Loopback]' if needed.
    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        loopback_devices = []
        default_device = None
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_output_device_info = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            #print(default_output_device_info)
            default_device = f"{default_output_device_info['name']} [Loopback]"
            #print(default_device_name)
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['hostApi'] == wasapi_info['index'] and device_info['maxInputChannels'] > 0:
                    device_entry = [device_info['name'], i]  # Store name and index as a list
                    if device_info.get('isLoopbackDevice', False):
                        loopback_devices.append(device_entry)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch audio devices: {str(e)}")
        finally:
            p.terminate()
        return loopback_devices, default_device

    def record_audio(self):
        """Captures audio from loopback without saving to a file and returns raw data as NumPy array."""
        p = pyaudio.PyAudio()
        capturing_device = None
        audio_frames = []
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            #print(wasapi_info)
            device_name = self.device_dropdown.get()
            device_index = self.get_device_index_by_name(device_name)
            capturing_device = p.get_device_info_by_index(device_index)

            def callback(in_data, frame_count, time_info, status):
                """Collects raw audio frames from the stream."""
                audio_frames.append(in_data)
                return (in_data, pyaudio.paContinue)

            with p.open(format=pyaudio.paInt16,
                        channels=capturing_device["maxInputChannels"],
                        rate=int(capturing_device["defaultSampleRate"]),
                        frames_per_buffer=CHUNK_SIZE,
                        input=True,
                        input_device_index=capturing_device["index"],
                        stream_callback=callback) as stream:
                time.sleep(DURATION)
        finally:
            p.terminate()
        
        raw_audio = np.frombuffer(b"".join(audio_frames), dtype=np.int16)

        # Convert NumPy array to WAV using pydub
        audio_segment = AudioSegment(
            raw_audio.tobytes(),
            frame_rate=int(capturing_device["defaultSampleRate"]),
            sample_width=2,  # 16-bit PCM (2 bytes per sample)
            channels=capturing_device["maxInputChannels"]
        )

        # Export to a BytesIO object in WAV format
        wav_buffer = BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_bytes = wav_buffer.getvalue()

        return wav_bytes  # Return the processed WAV bytes

    async def recognize_song(self, audio_data):
        shazam = Shazam()
        result = await shazam.recognize(data=audio_data)
        self.animating = False
        self.display_result(result)

    def start_recognition(self):
        def recognition_thread():
            asyncio.set_event_loop(asyncio.new_event_loop())
            audio_data = self.record_audio()
            if audio_data is not None:
                asyncio.run(self.recognize_song(audio_data))

        thread = threading.Thread(target=recognition_thread)
        thread.start()

    def display_result(self, result):
        if "track" in result:
            track = result["track"]
            name = track.get("title", "Unknown")
            artist = track.get("subtitle", "Unknown")
            album = track.get("sections", [{}])[0].get("metadata", [{}])[0].get("text", "Unknown")
            year = next((m["text"] for m in track.get("sections", [{}])[0].get("metadata", []) if "year" in m.get("title", "").lower()), "Unknown")
            image_url = track.get("images", {}).get("coverarthq", "")
            shazam_url = track.get("url", "")

            self.show_info_popup(name, artist, album, year, image_url, shazam_url)
        else:
            messagebox.showerror("Not Found", "No match found!")

    def show_info_popup(self, name, artist, album, year, image_url, shazam_url):
        popup = tk.Toplevel(self.root)
        popup.title("Song Identified")
        popup.geometry("600x500")

        # Create a function to add Text widgets properly
        def create_text_widget(label_text, content, is_link=False):
            frame = ttk.Frame(popup)
            frame.pack(pady=5, fill=tk.X)
            label = ttk.Label(frame, text=f"{label_text}:")
            label.pack(side=tk.LEFT, padx=5)
            text = tk.Text(frame, height=1, width=30, wrap='none', borderwidth=0, highlightthickness=0)
            text.insert("end", content)
            text.configure(state='disabled', inactiveselectbackground=text.cget("selectbackground"))
            text.pack(side=tk.LEFT, expand=True, fill=tk.X)
            if is_link:
                text.configure(cursor="hand2", fg="blue")
                text.bind("<Button-1>", lambda e, url=content: webbrowser.open(url))

        create_text_widget("Song", name)
        create_text_widget("Artist", artist)
        create_text_widget("Album", album)
        create_text_widget("Year", year)
        create_text_widget("Shazam Link", shazam_url, is_link=True)

        if image_url:
            response = requests.get(image_url)
            img_data = response.content
            image = Image.open(io.BytesIO(img_data))
            image = image.resize((250, 250), Image.LANCZOS)
            img = ImageTk.PhotoImage(image)
            img_label = ttk.Label(popup, image=img)
            img_label.image = img
            img_label.pack(pady=10)

        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = ShazamApp(root)
    root.mainloop()