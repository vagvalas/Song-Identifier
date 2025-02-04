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


# To be added (or already added :P)

1. A nicer UI
2. Selection multiple devices, both input and output (loopback) not defaulting just to default output device.
3. A way to capture audio to bit stream , so no need for file
4. A nicer animation
5. More info on window
6. Check to not crash if not treated well
7. A LINK!
... more.

# Thoughts

It will be ported to an all-in-one .exe for usage on any windows machines.

# Why PYTHON then and not C#

The library need for identification Shazamio (https://github.com/shazamio/ShazamIO ) was only written in Python , else the C# will be preferred. 
