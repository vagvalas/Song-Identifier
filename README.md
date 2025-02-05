# Song-Identifier
Match any song which playing through your pc speakers and more

# WHY?

The answer is located that i sit in PC for work a lot of hours, and many many times, i listen to some local radio, which is just a stream , and want to know whats the song called.

# Competitors

All the other solutions was to capture audio from input devices, and i had to make a whole procedure on looping my output, through a audio mix, and outputing in a virtual input (voicemeeter is called the software , take a look, very powerful)

## What it does (for now v.0.1)

It just detects the audio from speakers (loopback) , (it only detects the default output device, and search for its loopback device)
records it to a small wav file and send it using Shazamio package library (https://github.com/shazamio/ShazamIO)
and returns a window with info.

Its just the basic functionallity, but more feauture will be added.

# Changelog:
v0.4:
--Actually not start the recognition if selected_device is not a device
--Fixed "Year" tag always to Unknown, wrong location was searched.
--More infos in result window
--Add a play button as shazamio also fetches a preview audio of identified song
--Added Icon.ico to new popup window
--Lot of debug messages for me

v0.3:
--Added Input devices
--Check to validate selection to not start if no device is seleted

v0.2.1:
--Added also image to button instead of "Recognize"
--Added animation when clicking the button

## First major update 
v0.2:
--Seperated thread for recognition
--Added detection for loopback devices
--Detched the wav file (converted to byte array)
--More infos on result window

v0.1 (first commit):
--Initial release

# To be added (or already added :P)

1. Transfer the Recognition process to a new thread for not hanging the whole app. (in v0.2)
2. A nicer UI (v0.4)
3. Selection multiple devices, both input and output (loopback) not defaulting just to default output device. (v0.3)
4. A way to capture audio to bit stream , so no need for file (v0.2)
5. A nicer animation (v0.2.1)
6. More info on window (v0.4)
7. Check to not crash if not treated well (bugs in all versions)
8. A LINK! (v0.2)
... more.

# Thoughts

It will be ported to an all-in-one .exe for usage on any windows machines.

# Why PYTHON then and not C#

The library need for identification Shazamio (https://github.com/shazamio/ShazamIO ) was only written in Python , else the C# will be preferred. 
