# Song-Identifier
Match any song which playing through your pc speakers and more

# WHY?

The answer is located that i sit in PC for work a lot of hours, and many many times, i listen to some local radio, which is just a stream , and want to know whats the song called.

# Competitors

All the other solutions was to capture audio from input devices, and i had to make a whole procedure on looping my output, through a audio mix, and outputing in a virtual input (voicemeeter is called the software , take a look, very powerful)

## What it does (~~for now v.0.1~~) v1.0:

Should also add images and screenshots:
1. It loads and searches for default playback device (e.g. Speakers)
2. It links it to the Loopback device (as it has the same name)
3. The button trigers the record audio to an array (4 seconds) and then sends to api to recognize
4. Returns a popup window with full infos and even Preview Audio.
Crash-free , even on not selecting device, and error handling of no result and not return values in API

~~It just detects the audio from speakers (loopback) , (it only detects the default output device, and search for its loopback device)~~
~~records it to a small wav file and send it using Shazamio package library (https://github.com/shazamio/ShazamIO)~~
~~and returns a window with info.~~

~~Its just the basic functionallity, but more feauture will be added.~~

## Changelog

### v1.0
- Code Cleanup
- Stable release
- All bugs fixed. Now checks everything (even to not re-trigger the recognition once it's started once)

### v0.4
- Actually not start the recognition if selected_device is not a device
- Fixed "Year" tag always to Unknown, wrong location was searched.
- More infos in result window
- Add a play button as shazamio also fetches a preview audio of identified song
- Added Icon.ico to new popup window
- Lot of debug messages for me

### v0.3
- Added Input devices
- Check to validate selection to not start if no device is selected

### v0.2.1
- Added also image to button instead of "Recognize"
- Added animation when clicking the button

### First Major Update
#### v0.2
- Separated thread for recognition
- Added detection for loopback devices
- Detached the wav file (converted to byte array)
- More infos on result window

### Initial Release
#### v0.1
- Initial release


# To be added (or already added :P)

1. Transfer the Recognition process to a new thread for not hanging the whole app. (in v0.2)
2. A nicer UI (v0.4)
3. Selection multiple devices, both input and output (loopback) not defaulting just to default output device. (v0.3)
4. A way to capture audio to bit stream , so no need for file (v0.2)
5. A nicer animation (v0.2.1)
6. More info on window (v0.4)
7. Check to not crash if not treated well (bugs in all versions) (v0.4, and v1.0)
8. A LINK! (v0.2)
... more.

# Thoughts

It will be ported to an all-in-one .exe for usage on any windows machines.

# Why PYTHON then and not C#

The library need for identification Shazamio (https://github.com/shazamio/ShazamIO ) was only written in Python , else the C# will be preferred. 
