from mutagen.mp3 import MP3

audio = MP3("apple_description.mp3")
print("Length (s):", audio.info.length)
print("Bitrate:", audio.info.bitrate)
print("Sample rate:", audio.info.sample_rate)

# "PCM" is an acronym with multiple meanings, including Pulse Code Modulation, a digital signal encoding technique