import asyncio
import pyaudiowpatch as pyaudio
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from shazamio import Shazam, Serialize
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
from pydub.playback import play
from pydub.playback import _play_with_simpleaudio as play_audio
import simpleaudio as sa

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
        #MAKE THE WINDOWS AROUND
        self.root = root
        self.root.title("Song Identifier")
        self.root.geometry("450x400")
        self.root.iconbitmap(resource_path("icon.ico"))

        #CALL GET_AUDIO_DEVICES to fetch devices
        self.loopback_devices, self.input_devices, self.default_device = self.get_audio_devices()

        # Initialize the Tkinter variable for the selected device
        self.selected_device = tk.StringVar(value="Select a device")
        print("1") # debug for me
        # Create UI widgets
        self.create_widgets()
        self.load_animation(resource_path("shaza_anim.gif"))  # Load the animation frames
        # Set default device if it's available in the loopback list
        if any(device[0] == self.default_device for device in self.loopback_devices):
            self.selected_device.set(self.default_device)
            print("3")
        elif self.loopback_devices:
            # Set the fallback to the name of the first loopback device
            self.selected_device.set(self.loopback_devices[0][0])  # Access the first element's name
    
    def validate_selection(self, event):
        # Get the current selection from the combobox directly
        current_selection = self.device_dropdown.get()
        print(f"Dropdown changed to: {current_selection}")  # Debug statement

        # Check if the selection is valid (not a separator)
        if "---" not in current_selection:
            self.selected_device.set(current_selection)
            print(f"Valid device selected: {self.selected_device.get()}")  # Debug statement
        else:
            # Reset to default or prompt selection
            self.selected_device.set(self.default_device) #set the default again to not crash
            print("Invalid selection, reset to default.")  # Debug statement

    def create_widgets(self):
        label = ttk.Label(self.root, text="Select Audio Source:")
        label.pack(pady=10)

        # Prepare device list with separators for categories
        loopback_device_names = [device[0] for device in self.loopback_devices]  # Extract names from loopback devices
        input_device_names = [device[0] for device in self.input_devices]  # Extract names from input devices

        # Combine the lists with headers for each category
        device_list = ["---LOOPBACK DEVICES---"] + loopback_device_names + ["---INPUT DEVICES---"] + input_device_names
        print("2")
        self.device_dropdown = ttk.Combobox(self.root, textvariable=self.selected_device, values=device_list, state="readonly", width=60)
        self.device_dropdown.pack()


        # Bind the selection event to validate_selection to handle updates
        self.device_dropdown.bind("<<ComboboxSelected>>", self.validate_selection)

        #all for LOGO#
        original_image = Image.open(resource_path("shaza_logo.png"))
        resized_image = original_image.resize((200, 200), Image.Resampling.LANCZOS)
        self.shazam_logo = ImageTk.PhotoImage(resized_image)
        self.recognize_button = ttk.Button(self.root, image=self.shazam_logo, command=self.start_recognition)
        self.recognize_button.pack(pady=20)

    def get_device_index_by_name(self, device_name):
        # Search in both loopback and input devices
        for device in self.loopback_devices + self.input_devices:
            if device[0] == device_name:  # Compare the name
                return device[1]  # Return the index
        return None  # Return None if not found

    # Note: In 'get_audio_devices', ensure 'default_device_name' is correctly identified and appended with '[Loopback]' if needed.
    def load_animation(self, gif_path):
        """Load all frames of the animated GIF into a list."""
        self.gif_frames = []
        frame_index = 0
        while True:
            try:
                frame = PhotoImage(file=gif_path, format=f"gif -index {frame_index}")
                self.gif_frames.append(frame)
                frame_index += 1
            except:
                break  # Stop loading when no more frames are available

    def animate(self, frame_index=0):
        """Loop through GIF frames to animate the button image."""
        if self.animating:
            frame = self.gif_frames[frame_index % len(self.gif_frames)]
            self.recognize_button.config(image=frame)
            self.recognize_button.image = frame  # Prevent garbage collection
            self.root.after(100, self.animate, frame_index + 1)
        else:
            self.recognize_button.config(image=self.shazam_logo)  # Reset to PNG

    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        loopback_devices = []
        input_devices = []
        default_device = None
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_output_device_info = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            #print(default_output_device_info)
            default_device = f"{default_output_device_info['name']} [Loopback]"
            #print(default_device)
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['hostApi'] == wasapi_info['index'] and device_info['maxInputChannels'] > 0:
                    device_entry = [device_info['name'], i]  # Store name and index as a list
                    if device_info.get('isLoopbackDevice', False):
                        loopback_devices.append(device_entry)
                    else:
                        input_devices.append(device_entry)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch audio devices: {str(e)}")
        finally:
            p.terminate()
        return loopback_devices, input_devices, default_device

    def record_audio(self):
        """Captures audio from loopback without saving to a file and returns raw data as NumPy array."""
        p = pyaudio.PyAudio()
        capturing_device = None
        audio_frames = []
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
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
        print(result) #debug to print whole json for finding values to extract
        self.display_result(result)

    def start_recognition(self):
        if self.selected_device.get() != "Select a device": #check for no device selection to not crash the app
            #it was from previous version, but still thinking if its better to let user choose device
            #refer. self.selected_device.set("Select a device")
            self.animating = True
            self.animate()  # Start animation
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
            sections = result["track"].get("sections", [])
            year = "Unknown"  # Default value if the year is not found

            # Ensure there's at least one section and it has metadata with at least three items
            if sections and len(sections) > 0 and "metadata" in sections[0] and len(sections[0]["metadata"]) >= 3:
                year = sections[0]["metadata"][2].get("text", "Unknown")  # Accessing the third metadata item's text
            hub = result["track"].get("hub", {})
            actions = hub.get("actions", [])
            
            uri = "Not found"  # Default if no matching uri is found
            for action in actions:
                if action.get("type") == "uri":
                    uri = action.get("uri", "Not found")
                    break  # Stop searching once the uri is found

            #print("URI:", uri)
            audio_uri = uri
            image_url = track.get("images", {}).get("coverarthq", "")
            shazam_url = track.get("url", "")  # Assuming the API provides a direct link

            self.show_info_popup(name, artist, album, year, image_url, shazam_url, audio_uri)
        else:
            messagebox.showerror("Not Found", "No match found!")

    def show_info_popup(self, name, artist, album, year, image_url, shazam_url, audio_uri):
        popup = tk.Toplevel(self.root)
        popup.title(name)
        popup.geometry("600x600")
        popup.iconbitmap(resource_path("icon.ico")) #add also an icon
        # Setup threading and audio control
        playback_thread = None
        play_obj = None

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

        def preview_audio():
            nonlocal play_obj
            try:
                # Download audio file data
                if audio_uri != "Not found": #check to not crash the preview button
                    response = requests.get(audio_uri)
                    audio_data = BytesIO(response.content)
                    
                    # Load the audio file using pydub
                    audio = AudioSegment.from_file(audio_data, format='mp4')  # Assume .m4a files use mp4 format
                    duration_ms = len(audio)
                    duration_s = duration_ms // 1000
                    print(duration_ms)
                    print(duration_s)
                    # Play the audio using pydub's play
                    play_obj = play_audio(audio)  # This returns a play object that can be stopped
                else:
                    messagebox.showerror("Not Found", "No preview is available")
            except Exception as e:
                print("Error playing audio:", e)
        
        def stop_audio():
            if play_obj:
                play_obj.stop()
        def start_playback():
            nonlocal playback_thread
            playback_thread = threading.Thread(target=preview_audio)
            playback_thread.start()

        # Button frame for side-by-side layout
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10, fill=tk.X)

        preview_button = ttk.Button(button_frame, text="Preview", command=start_playback)
        preview_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        stop_button = ttk.Button(button_frame, text="Stop", command=stop_audio)
        stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(popup, text="Close", command=lambda: [stop_audio(), popup.destroy()]).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = ShazamApp(root)
    root.mainloop()